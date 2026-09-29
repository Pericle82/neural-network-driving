"""Il mondo che il server fa girare e trasmette alla UI.

Sceglie la modalità in base a quello che hai già implementato:
  - "demo":   Car.step non esiste ancora → un'auto fantasma segue la linea centrale
  - "manual": tappa 1 fatta → guidi con la tastiera, i bordi ti eliminano
Dalla tappa 2 aggiunge i raggi; le modalità "training" e "replay" arrivano con le tappe 5 e 6.
"""

from __future__ import annotations

import math

import numpy as np

from sim import car as car_mod
from sim import sensors as sensors_mod
from sim.track import Track, build_track

from .protocol import CarMsg, InputMsg, State, Stats

DEMO_SPEED = 180.0  # unità/s dell'auto fantasma
RESPAWN_AFTER = 1.5  # secondi da "morta" prima di ripartire dal via


def _implemented(fn, *args) -> bool:
    try:
        fn(*args)
        return True
    except NotImplementedError:
        return False
    except Exception:
        return True  # implementato ma con errori: lascia che emergano durante la corsa


class World:
    def __init__(self, track: Track | None = None):
        self.track = track or build_track()
        self.walls = self.track.walls()
        self.controls = car_mod.Controls()
        self.reset()

    def reset(self) -> None:
        x, y, h = self.track.start_pose()
        self.car = car_mod.Car(x=x, y=y, heading=h)
        self.t = 0.0
        self._demo_s = 0.0
        self._dead_for = 0.0
        probe = car_mod.Car(x=x, y=y, heading=h)
        self.mode = "manual" if _implemented(probe.step, car_mod.Controls(), 0.0) else "demo"
        self.has_sensors = _implemented(sensors_mod.read_sensors, x, y, h, self.walls)

    def apply_input(self, msg: InputMsg) -> None:
        self.controls = car_mod.Controls(
            steering=msg.steering, throttle=msg.throttle, brake=msg.brake, handbrake=msg.handbrake
        )

    def step(self, dt: float) -> None:
        self.t += dt
        if self.mode == "demo":
            self._demo_step(dt)
            return
        if self.car.alive:
            self.car.step(self.controls, dt)
            if car_mod.collides(self.car, self.walls):
                self.car.alive = False
                self.car.speed = 0.0
        else:
            self._dead_for += dt
            if self._dead_for >= RESPAWN_AFTER:
                self.reset()

    def _demo_step(self, dt: float) -> None:
        """Auto fantasma: scorre la linea centrale a velocità costante."""
        c = self.track.center
        seg = np.linalg.norm(np.roll(c, -1, axis=0) - c, axis=1)
        self._demo_s = (self._demo_s + DEMO_SPEED * dt) % seg.sum()
        i = int(np.searchsorted(np.cumsum(seg), self._demo_s))
        i = min(i, len(c) - 1)
        a, b = c[i], c[(i + 1) % len(c)]
        self.car.x, self.car.y = float(a[0]), float(a[1])
        self.car.heading = math.atan2(b[1] - a[1], b[0] - a[0])
        self.car.speed = DEMO_SPEED

    def snapshot(self) -> State:
        car = self.car
        rays = readings = None
        if self.has_sensors:
            r, hits = sensors_mod.read_sensors(car.x, car.y, car.heading, self.walls)
            rays = hits.round(1).tolist()
            readings = [*np.round(r, 3).tolist(), round(car.speed / car_mod.MAX_SPEED, 3)]
        return State(
            t=round(self.t, 3),
            cars=[CarMsg(id=0, x=car.x, y=car.y, heading=car.heading, speed=car.speed, alive=car.alive)],
            focus=0,
            rays=rays,
            readings=readings,
            stats=Stats(mode=self.mode, alive=int(car.alive)),
        )
