"""Tappa 2 — I sensori a raggio (raycasting).

Obiettivo: 7 raggi dal muso dell'auto che misurano la distanza dal bordo più vicino.
Teoria: indice didattico, Parte 1, punto 5.
"""

from __future__ import annotations

import numpy as np

# Angoli dei raggi rispetto al muso, come nel video.
RAY_ANGLES_DEG = (-65, -20, -10, 0, 10, 20, 65)
RAY_LENGTH = 260.0   # portata massima: oltre, il raggio "vede libero"


def ray_segment_distance(origin: np.ndarray, direction: np.ndarray, seg: np.ndarray) -> float | None:
    """Distanza lungo il raggio fino al segmento `seg` ([[x1, y1], [x2, y2]]), o None.

    TODO(step-02): risolvi origin + t*direction = a + u*(b - a)
      con t >= 0 e 0 <= u <= 1 (sistema 2x2, regola di Cramer).
      Se il denominatore è ~0 i due sono paralleli: None.
    """
    raise NotImplementedError("tappa 2: ray_segment_distance")


def read_sensors(x: float, y: float, heading: float, walls: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Letture normalizzate e punti d'impatto.

    Restituisce:
      readings: (7,) in [0, 1]  -> min(distanza / RAY_LENGTH, 1)
      hits:     (7, 2)          -> punto d'impatto (o fine del raggio), per disegnarlo in UI

    TODO(step-02): per ogni angolo, direzione = (cos(heading+a), sin(heading+a)),
      distanza minima su tutti i `walls`.
    """
    raise NotImplementedError("tappa 2: read_sensors")
