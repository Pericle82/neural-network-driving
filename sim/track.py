"""La pista: geometria pronta all'uso (fornita, non è un esercizio).

Idea: la pista si descrive con pochi *punti di controllo* della linea centrale.
Una spline di Catmull-Rom chiusa li raccorda in una curva morbida, che viene
campionata in N punti. Spostando ogni punto lungo la normale di ±larghezza/2
si ottengono i due bordi, cioè i "muri" contro cui l'auto non deve sbattere.

    punti di controllo ──spline──▶ linea centrale ──normali──▶ bordo interno / esterno

Coordinate: unità del mondo, asse x verso destra, asse y verso il BASSO
(come lo schermo), angoli in radianti misurati da x verso y.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Pista di default: un circuito chiuso con curve a S, simile a quello del video.
DEFAULT_CONTROL_POINTS: list[tuple[float, float]] = [
    (160, 140), (400, 110), (570, 190), (740, 120), (890, 180),
    (930, 420), (850, 560), (620, 520), (430, 620), (200, 590),
    (110, 380),
]
DEFAULT_WIDTH = 80.0


@dataclass(frozen=True)
class Track:
    """Geometria della pista. Tutti gli array hanno forma (N, 2) salvo indicazione."""

    center: np.ndarray      # punti della linea centrale, in ordine di percorrenza
    left: np.ndarray        # bordo a sinistra del senso di marcia
    right: np.ndarray       # bordo a destra del senso di marcia
    curvature: np.ndarray   # (N,) curvatura con segno in ogni punto (1/raggio)
    width: float

    @property
    def n(self) -> int:
        return len(self.center)

    def walls(self) -> np.ndarray:
        """Tutti i segmenti dei bordi, forma (2N, 2, 2): [[x1, y1], [x2, y2]].

        Serviranno alla tappa 1 (collisioni) e alla tappa 2 (raggi dei sensori).
        """
        segs = []
        for border in (self.left, self.right):
            nxt = np.roll(border, -1, axis=0)
            segs.append(np.stack([border, nxt], axis=1))
        return np.concatenate(segs, axis=0)

    def checkpoints(self, every: int = 10) -> np.ndarray:
        """Traguardi intermedi: segmenti trasversali da bordo a bordo, forma (K, 2, 2).

        Contarli in ordine misura quanto l'auto è andata avanti (tappa 5: fitness).
        """
        idx = np.arange(0, self.n, every)
        return np.stack([self.left[idx], self.right[idx]], axis=1)

    def start_pose(self) -> tuple[float, float, float]:
        """Posizione (x, y) e orientamento iniziale dell'auto: primo punto, lungo la tangente."""
        d = self.center[1] - self.center[0]
        return float(self.center[0, 0]), float(self.center[0, 1]), float(np.arctan2(d[1], d[0]))

    def to_dict(self) -> dict:
        """Forma serializzabile in JSON, inviata alla UI nel messaggio `hello`."""
        return {
            "center": self.center.round(2).tolist(),
            "left": self.left.round(2).tolist(),
            "right": self.right.round(2).tolist(),
            "curvature": self.curvature.round(5).tolist(),
            "width": self.width,
        }


def catmull_rom_closed(points: np.ndarray, samples_per_segment: int) -> np.ndarray:
    """Campiona una spline di Catmull-Rom chiusa che passa per tutti i `points`."""
    p = np.asarray(points, dtype=float)
    t = np.linspace(0.0, 1.0, samples_per_segment, endpoint=False)[:, None]
    t2, t3 = t * t, t * t * t
    out = []
    for i in range(len(p)):
        p0, p1, p2, p3 = p[i - 1], p[i], p[(i + 1) % len(p)], p[(i + 2) % len(p)]
        out.append(
            0.5 * ((2 * p1)
                   + (-p0 + p2) * t
                   + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                   + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
        )
    return np.concatenate(out, axis=0)


def build_track(
    control_points: list[tuple[float, float]] = DEFAULT_CONTROL_POINTS,
    width: float = DEFAULT_WIDTH,
    samples_per_segment: int = 24,
) -> Track:
    center = catmull_rom_closed(np.array(control_points), samples_per_segment)

    # Tangente con differenze centrate (la pista è chiusa: np.roll fa da "giro").
    tangent = np.roll(center, -1, axis=0) - np.roll(center, 1, axis=0)
    tangent /= np.linalg.norm(tangent, axis=1, keepdims=True)
    # Normale a sinistra del senso di marcia, con y verso il basso: (ty, -tx).
    normal = np.stack([tangent[:, 1], -tangent[:, 0]], axis=1)

    left = center + normal * (width / 2)
    right = center - normal * (width / 2)

    # Curvatura con segno: variazione dell'angolo della tangente per unità di lunghezza.
    heading = np.unwrap(np.arctan2(tangent[:, 1], tangent[:, 0]))
    dh = np.roll(heading, -1) - heading
    dh = (dh + np.pi) % (2 * np.pi) - np.pi
    ds = np.linalg.norm(np.roll(center, -1, axis=0) - center, axis=1)
    curvature = dh / ds

    return Track(center=center, left=left, right=right, curvature=curvature, width=width)
