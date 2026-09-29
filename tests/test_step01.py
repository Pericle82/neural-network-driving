"""Tappa 1 — fisica dell'auto e collisioni.

Ogni test controlla un comportamento che ti aspetteresti da un'auto vera.
Se un test fallisce, leggi il suo nome: dice cosa l'auto dovrebbe fare.
"""

import math

import numpy as np
import pytest

from sim.car import (
    MAX_SPEED,
    Car,
    Controls,
    collides,
    segments_intersect,
)
from sim.track import build_track

DT = 1 / 60


def drive(car: Car, controls: Controls, seconds: float) -> Car:
    for _ in range(round(seconds / DT)):
        car.step(controls, DT)
    return car


# ── Velocità ────────────────────────────────────────────────────────────────

def test_throttle_accelerates_from_standstill():
    car = drive(Car(0, 0, 0), Controls(throttle=1), 1.0)
    assert 100 < car.speed < MAX_SPEED


def test_speed_never_exceeds_max_speed():
    car = drive(Car(0, 0, 0), Controls(throttle=1), 30.0)
    assert car.speed <= MAX_SPEED + 1e-9


def test_coasting_slows_down_because_of_drag():
    car = Car(0, 0, 0, speed=200)
    drive(car, Controls(), 1.0)
    assert 0 < car.speed < 200


def test_brake_stops_the_car_without_reversing():
    car = drive(Car(0, 0, 0, speed=200), Controls(brake=1), 3.0)
    assert car.speed == 0.0


def test_controls_out_of_range_are_clamped():
    a = drive(Car(0, 0, 0), Controls(throttle=5, steering=-9), 1.0)
    b = drive(Car(0, 0, 0), Controls(throttle=1, steering=-1), 1.0)
    assert (a.x, a.y, a.speed) == pytest.approx((b.x, b.y, b.speed))


# ── Direzione ───────────────────────────────────────────────────────────────

def test_moves_along_heading():
    car = drive(Car(0, 0, heading=math.pi / 2, speed=100), Controls(throttle=0.3), 0.5)
    assert abs(car.x) < 1e-6 and car.y > 0   # heading π/2 = verso il basso (+y)


def test_positive_steering_turns_right_on_screen():
    car = drive(Car(0, 0, 0, speed=150), Controls(steering=1, throttle=0.5), 0.3)
    assert car.heading > 0 and car.y > 0     # y verso il basso: curva a destra


def test_standing_car_cannot_rotate():
    car = drive(Car(0, 0, 0), Controls(steering=1), 1.0)
    assert car.heading == 0.0 and (car.x, car.y) == (0, 0)


def test_turning_radius_grows_with_speed():
    """A velocità alta lo sterzo rende meno: bisogna frenare prima delle curve."""
    def radius(speed: float) -> float:
        car = Car(0, 0, 0, speed=speed)
        car.step(Controls(steering=1), DT)
        return car.speed / (car.heading / DT)
    assert radius(300) > radius(80) * 1.5


def test_handbrake_turns_tighter_and_loses_speed():
    normal = drive(Car(0, 0, 0, speed=200), Controls(steering=1), 0.5)
    hand = drive(Car(0, 0, 0, speed=200), Controls(steering=1, handbrake=True), 0.5)
    assert hand.speed < normal.speed
    assert hand.heading > normal.heading * 1.1


def test_heading_stays_in_minus_pi_pi():
    car = drive(Car(0, 0, 0, speed=150), Controls(steering=1, throttle=0.5), 20.0)
    assert -math.pi <= car.heading <= math.pi


def test_physics_is_deterministic():
    runs = [drive(Car(10, 20, 0.3), Controls(steering=0.4, throttle=0.8), 2.0) for _ in range(2)]
    assert (runs[0].x, runs[0].y, runs[0].heading) == (runs[1].x, runs[1].y, runs[1].heading)


# ── Collisioni ──────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "p1, p2, q1, q2, expected",
    [
        ((0, 0), (10, 10), (0, 10), (10, 0), True),     # una X
        ((0, 0), (10, 0), (0, 5), (10, 5), False),      # paralleli
        ((0, 0), (10, 0), (5, 1), (5, 10), False),      # q passa sopra, senza toccare
        ((0, 0), (4, 0), (5, -5), (5, 5), False),       # stessa retta, ma p finisce prima
        ((0, 0), (10, 0), (5, -1), (5, 1), True),       # croce corta
    ],
)
def test_segments_intersect(p1, p2, q1, q2, expected):
    arr = [np.array(p, dtype=float) for p in (p1, p2, q1, q2)]
    assert segments_intersect(*arr) is expected


def test_car_at_start_does_not_collide():
    track = build_track()
    x, y, h = track.start_pose()
    assert not collides(Car(x, y, h), track.walls())


def test_car_on_the_border_collides():
    track = build_track()
    x, y = track.left[40]
    assert collides(Car(float(x), float(y), 0.0), track.walls())


def test_full_throttle_straight_ahead_hits_a_wall():
    """Senza sterzare, prima o poi la pista curva e l'auto esce."""
    track = build_track()
    walls = track.walls()
    car = Car(*track.start_pose())
    for _ in range(round(5 / DT)):
        car.step(Controls(throttle=1), DT)
        if collides(car, walls):
            break
    else:
        pytest.fail("l'auto ha viaggiato 5 secondi dritta senza toccare un bordo")
