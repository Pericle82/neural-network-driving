"""Il contratto tra simulazione (Python) e UI (browser).

È il confine tra i due mondi: finché questi messaggi restano stabili, Python e UI
evolvono in modo indipendente. Documentazione leggibile in docs/protocol.md.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

PROTOCOL_VERSION = 1


# ── Server → browser ────────────────────────────────────────────────────────

class TrackMsg(BaseModel):
    center: list[list[float]]
    left: list[list[float]]
    right: list[list[float]]
    curvature: list[float]
    width: float


class Hello(BaseModel):
    type: Literal["hello"] = "hello"
    v: int = PROTOCOL_VERSION
    track: TrackMsg
    layers: list[int]


class CarMsg(BaseModel):
    id: int
    x: float
    y: float
    heading: float
    speed: float
    alive: bool


class NetworkMsg(BaseModel):
    weights: list[list[list[float]]]   # una matrice (n_out, n_in) per strato
    activations: list[list[float]]     # un vettore per strato, input compreso


class Stats(BaseModel):
    mode: Literal["demo", "manual", "training", "replay"]
    generation: int = 0
    alive: int = 0
    best_fitness: float = 0.0


class State(BaseModel):
    type: Literal["state"] = "state"
    t: float
    cars: list[CarMsg]
    focus: int | None = None               # id dell'auto seguita dalla camera
    rays: list[list[float]] | None = None  # punti d'impatto dei raggi dell'auto seguita
    readings: list[float] | None = None    # le 8 letture in ingresso alla rete
    outputs: list[float] | None = None     # i 4 comandi in uscita
    network: NetworkMsg | None = None
    stats: Stats


# ── Browser → server ────────────────────────────────────────────────────────

class InputMsg(BaseModel):
    type: Literal["input"] = "input"
    steering: float = 0.0
    throttle: float = 0.0
    brake: float = 0.0
    handbrake: bool = False


class ControlMsg(BaseModel):
    type: Literal["control"] = "control"
    action: Literal["pause", "resume", "reset", "speed"]
    value: float | None = None             # moltiplicatore per action="speed"
