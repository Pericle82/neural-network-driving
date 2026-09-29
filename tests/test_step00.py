"""Tappa 0 — lo scheletro funziona: pista valida e server che risponde.

Questi test passano già: sono il punto di partenza verde del corso.
"""

import numpy as np
from fastapi.testclient import TestClient

from server.app import app
from sim.track import build_track


def test_track_is_closed_loop_with_two_borders():
    t = build_track()
    assert t.center.shape == t.left.shape == t.right.shape
    # distanza tra bordi = larghezza pista
    gap = np.linalg.norm(t.left - t.right, axis=1)
    assert np.allclose(gap, t.width, atol=1e-6)
    # l'ultimo punto è vicino al primo: il giro si chiude
    step = np.linalg.norm(np.diff(t.center, axis=0), axis=1).max()
    assert np.linalg.norm(t.center[-1] - t.center[0]) <= step * 1.5


def test_curves_are_wider_than_half_track():
    """Se una curva ha raggio < metà larghezza, il bordo interno si incrocia su se stesso."""
    t = build_track()
    min_radius = 1 / np.abs(t.curvature).max()
    assert min_radius > t.width / 2


def test_walls_and_checkpoints_shapes():
    t = build_track()
    assert t.walls().shape == (2 * t.n, 2, 2)
    cps = t.checkpoints(every=10)
    assert cps.shape[1:] == (2, 2) and len(cps) == int(np.ceil(t.n / 10))


def test_websocket_sends_hello_then_state():
    with TestClient(app).websocket_connect("/ws") as ws:
        hello = ws.receive_json()
        assert hello["type"] == "hello" and hello["v"] == 1
        assert hello["layers"] == [8, 6, 4]
        assert len(hello["track"]["left"]) == len(hello["track"]["right"])
        state = ws.receive_json()
        assert state["type"] == "state"
        assert state["stats"]["mode"] in ("demo", "manual")
        assert len(state["cars"]) == 1
