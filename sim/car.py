"""Tappa 1 — L'auto: fisica e collisioni.

Obiettivo: un'auto che si muove in modo credibile e "muore" quando tocca un bordo.
Teoria: indice didattico, Parte 1, punti 3 e 4.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Parametri fisici di partenza: sentiti libero di tararli.
MAX_SPEED = 320.0        # unità/s
ACCELERATION = 220.0     # unità/s²
BRAKE_DECEL = 420.0      # unità/s²
DRAG = 0.6               # attrito proporzionale alla velocità (1/s)
WHEELBASE = 26.0         # passo: distanza tra asse anteriore e posteriore
MAX_STEER = 0.55         # angolo massimo delle ruote anteriori (rad), da fermi
STEER_AT_MAX_SPEED = 0.4 # a velocità massima lo sterzo utile scende al 40%
HANDBRAKE_TURN = 1.6     # freno a mano: il posteriore scivola, l'auto gira di più...
HANDBRAKE_DRAG = 3.0     # ...ma perde velocità molto più in fretta
CAR_LENGTH = 30.0
CAR_WIDTH = 14.0


@dataclass
class Controls:
    """I 4 comandi, gli stessi che più avanti produrrà la rete neurale."""

    steering: float = 0.0    # [-1, 1]: -1 tutto a sinistra, +1 tutto a destra
    throttle: float = 0.0    # [0, 1]
    brake: float = 0.0       # [0, 1]
    handbrake: bool = False


@dataclass
class Car:
    x: float
    y: float
    heading: float           # radianti, 0 = verso +x
    speed: float = 0.0
    alive: bool = True

    def step(self, controls: Controls, dt: float) -> None:
        """Avanza la fisica di `dt` secondi.

        TODO(step-01): implementa il modello cinematico "a bicicletta".
          1. Limita i comandi: steering in [-1, 1], throttle e brake in [0, 1].
          2. Velocità: + ACCELERATION*throttle - BRAKE_DECEL*brake - attrito*speed,
             con attrito = DRAG (moltiplicato per HANDBRAKE_DRAG col freno a mano).
             Limita a [0, MAX_SPEED]: niente retromarcia.
          3. Sterzo: più vai veloce, meno puoi sterzare (come su un'auto vera):
             delta = steering * MAX_STEER * (1 - (1 - STEER_AT_MAX_SPEED) * speed / MAX_SPEED)
          4. Velocità angolare: omega = speed / WHEELBASE * tan(delta);
             col freno a mano moltiplica per HANDBRAKE_TURN.
          5. heading += omega*dt; x += cos(heading)*speed*dt; y += sin(heading)*speed*dt.
        Nota: con y verso il basso, heading che cresce = curva a DESTRA sullo schermo.
        Verifica: make test STEP=1
        """
        raise NotImplementedError("tappa 1: Car.step")

    def corners(self) -> np.ndarray:
        """I 4 vertici del rettangolo dell'auto, forma (4, 2). Fornito."""
        c, s = np.cos(self.heading), np.sin(self.heading)
        fwd = np.array([c, s]) * CAR_LENGTH / 2
        side = np.array([-s, c]) * CAR_WIDTH / 2
        p = np.array([self.x, self.y])
        return np.array([p + fwd + side, p + fwd - side, p - fwd - side, p - fwd + side])


def segments_intersect(p1: np.ndarray, p2: np.ndarray, q1: np.ndarray, q2: np.ndarray) -> bool:
    """True se il segmento p1-p2 interseca q1-q2.

    TODO(step-01): usa il test dell'orientamento (prodotto vettoriale 2D):
      i due segmenti si intersecano se q1 e q2 stanno da parti opposte di p1-p2
      E p1 e p2 stanno da parti opposte di q1-q2.
    """
    raise NotImplementedError("tappa 1: segments_intersect")


def collides(car: Car, walls: np.ndarray) -> bool:
    """True se un lato del rettangolo dell'auto tocca un segmento dei bordi.

    TODO(step-01): controlla i 4 lati di `car.corners()` contro tutti i `walls`
    (forma (M, 2, 2), vedi Track.walls). Suggerimento: scarta prima i muri lontani.
    """
    raise NotImplementedError("tappa 1: collides")
