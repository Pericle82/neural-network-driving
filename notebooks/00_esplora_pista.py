# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Tappa 0 — Esplora la pista
#
# Questo notebook non contiene esercizi: serve a verificare che l'ambiente funzioni
# e a prendere confidenza con la geometria su cui guiderà l'auto.
#
# **Regola del corso:** la logica vive nei moduli `sim/`, il notebook la importa
# e ci sperimenta. Così il notebook non accumula stato nascosto e i test possono
# verificare lo stesso codice che usi qui.

# %%
import matplotlib.pyplot as plt
import numpy as np

from sim.track import build_track

track = build_track()
print(f"punti della linea centrale: {track.n}, larghezza: {track.width}")

# %% [markdown]
# ## I due bordi sono i "muri"
#
# Ogni punto della linea centrale viene spostato di ±larghezza/2 lungo la normale.
# I segmenti tra punti consecutivi dei bordi sono ciò che i sensori "vedranno" (tappa 2)
# e che l'auto non deve toccare (tappa 1).

# %%
fig, ax = plt.subplots(figsize=(9, 6))
for border in (track.left, track.right):
    closed = np.vstack([border, border[:1]])
    ax.plot(closed[:, 0], closed[:, 1], color="black")
ax.plot(track.center[:, 0], track.center[:, 1], "--", lw=0.6, label="linea centrale")
for (a, b) in track.checkpoints(every=10):
    ax.plot([a[0], b[0]], [a[1], b[1]], color="tab:orange", lw=0.8)
x, y, h = track.start_pose()
ax.arrow(x, y, 40 * np.cos(h), 40 * np.sin(h), width=4, color="tab:green")
ax.invert_yaxis()  # y verso il basso, come sullo schermo
ax.set_aspect("equal")
ax.set_title("Pista, checkpoint (arancio) e partenza (verde)")
ax.legend()
plt.show()

# %% [markdown]
# ## Curvatura: dove servono i cordoli
#
# La curvatura è l'inverso del raggio della curva. Dove è alta, la UI disegna i
# cordoli bianco-rossi. **Prova:** cambia un punto in `DEFAULT_CONTROL_POINTS` e
# guarda come cambia il grafico; se il raggio minimo scende sotto metà larghezza,
# il test `test_curves_are_wider_than_half_track` fallisce. Perché?

# %%
fig, ax = plt.subplots(figsize=(9, 3))
ax.plot(track.curvature)
ax.axhline(0, color="grey", lw=0.5)
ax.set_xlabel("indice del punto lungo la pista")
ax.set_ylabel("curvatura (1/unità)")
plt.show()
print(f"raggio minimo: {1 / np.abs(track.curvature).max():.1f} (metà larghezza: {track.width / 2})")
