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
# # Tappa 1 — Laboratorio di fisica dell'auto
#
# Questo notebook funziona **dopo** che hai implementato `Car.step`, `segments_intersect`
# e `collides` in `sim/car.py`. Serve a *vedere* il modello, non solo a farlo passare nei test.
#
# L'idea del modello "a bicicletta": le due ruote anteriori diventano una sola, e così le
# posteriori. L'auto gira attorno a un punto sulla retta dell'asse posteriore, con raggio
# `R = WHEELBASE / tan(delta)`. Quindi la velocità angolare è `omega = speed / R`.

# %%
import matplotlib.pyplot as plt
import numpy as np

from sim import car as car_mod
from sim.car import Car, Controls, collides
from sim.track import build_track

DT = 1 / 60


def trajectory(car: Car, controls: Controls, seconds: float) -> np.ndarray:
    pts = []
    for _ in range(round(seconds / DT)):
        car.step(controls, DT)
        pts.append((car.x, car.y))
    return np.array(pts)


# %% [markdown]
# ## Stesso sterzo, velocità diverse
#
# Con lo sterzo tutto a destra, un'auto lenta chiude il cerchio stretto; una veloce no,
# perché lo sterzo utile cala con la velocità (`STEER_AT_MAX_SPEED`). È il motivo per cui,
# più avanti, la rete dovrà imparare a **frenare prima delle curve**.

# %%
fig, ax = plt.subplots(figsize=(7, 7))
for speed in (60, 150, 250, 320):
    # throttle calibrato per mantenere la velocità costante contro l'attrito
    keep = car_mod.DRAG * speed / car_mod.ACCELERATION
    path = trajectory(Car(0, 0, 0, speed=speed), Controls(steering=1, throttle=keep), 3.0)
    ax.plot(path[:, 0], path[:, 1], label=f"{speed} unità/s")
ax.invert_yaxis()
ax.set_aspect("equal")
ax.set_title("Sterzo = +1 per 3 secondi (y verso il basso: curva a destra)")
ax.legend()
plt.show()

# %% [markdown]
# ## Il freno a mano
#
# Il posteriore perde aderenza: l'auto gira molto di più ma rallenta in fretta.
# **Prova:** cambia `HANDBRAKE_TURN` e `HANDBRAKE_DRAG` in `sim/car.py` e riesegui.

# %%
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))
for hb in (False, True):
    car = Car(0, 0, 0, speed=250)
    xs, speeds = [], []
    for _ in range(round(1.2 / DT)):
        car.step(Controls(steering=1, handbrake=hb), DT)
        xs.append((car.x, car.y))
        speeds.append(car.speed)
    xs = np.array(xs)
    label = "freno a mano" if hb else "normale"
    a1.plot(xs[:, 0], xs[:, 1], label=label)
    a2.plot(np.arange(len(speeds)) * DT, speeds, label=label)
a1.invert_yaxis(); a1.set_aspect("equal"); a1.set_title("traiettoria"); a1.legend()
a2.set_xlabel("secondi"); a2.set_ylabel("velocità"); a2.set_title("velocità"); a2.legend()
plt.show()

# %% [markdown]
# ## Collisioni: dove finisce un'auto che va dritta?
#
# Tutto gas, niente sterzo: l'auto esce alla prima curva. Il punto rosso è dove
# `collides` diventa vero. Questo è esattamente il problema che la rete dovrà risolvere.

# %%
track = build_track()
walls = track.walls()
car = Car(*track.start_pose())
path = []
while not collides(car, walls):
    car.step(Controls(throttle=1), DT)
    path.append((car.x, car.y))
path = np.array(path)

fig, ax = plt.subplots(figsize=(9, 6))
for border in (track.left, track.right):
    closed = np.vstack([border, border[:1]])
    ax.plot(closed[:, 0], closed[:, 1], color="black")
ax.plot(path[:, 0], path[:, 1], color="tab:green")
ax.scatter(*path[-1], color="tab:red", zorder=3, s=40)
corners = np.vstack([car.corners(), car.corners()[:1]])
ax.plot(corners[:, 0], corners[:, 1], color="tab:red")
ax.invert_yaxis()
ax.set_aspect("equal")
ax.set_title(f"Uscita di pista dopo {len(path) * DT:.2f} s")
plt.show()

# %% [markdown]
# ## Prova tu
#
# 1. Scrivi un "pilota a regole" che sterza verso il punto successivo della linea centrale
#    (`track.center`) e guarda se completa il giro. È barare: conosce la pista intera.
#    La rete, invece, vedrà solo i 7 raggi della tappa 2.
# 2. Avvia `make dev` e guida con le frecce: senti la differenza tra curva lenta e veloce?
