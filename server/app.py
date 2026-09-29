"""Server di simulazione: fa girare il mondo e lo trasmette alla UI via WebSocket.

Avvio: make server  (oppure: uv run uvicorn server.app:app --reload)
"""

from __future__ import annotations

import asyncio
import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import TypeAdapter

from sim.nn import LAYERS

from .protocol import ControlMsg, Hello, InputMsg, TrackMsg
from .world import World

PHYSICS_DT = 1 / 60      # passo fisso di fisica (Parte 1, punto 1)
SEND_EVERY = 2           # un messaggio "state" ogni 2 passi → 30 al secondo

app = FastAPI(title="neural-network-driving")
_incoming = TypeAdapter(InputMsg | ControlMsg)


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.websocket("/ws")
async def ws(socket: WebSocket) -> None:
    await socket.accept()
    world = World()
    await socket.send_text(Hello(track=TrackMsg(**world.track.to_dict()), layers=list(LAYERS)).model_dump_json())

    state = {"paused": False, "speed": 1.0}

    async def receive() -> None:
        while True:
            msg = _incoming.validate_python(json.loads(await socket.receive_text()))
            if isinstance(msg, InputMsg):
                world.apply_input(msg)
            elif msg.action == "reset":
                world.reset()
            elif msg.action in ("pause", "resume"):
                state["paused"] = msg.action == "pause"
            elif msg.action == "speed" and msg.value:
                state["speed"] = max(0.25, min(msg.value, 100.0))

    receiver = asyncio.create_task(receive())
    try:
        tick = 0
        while not receiver.done():
            if not state["paused"]:
                # A velocità x10 si fanno 10 passi di fisica per ogni passo reale.
                for _ in range(max(1, round(state["speed"]))):
                    world.step(PHYSICS_DT)
                tick += 1
                if tick % SEND_EVERY == 0:
                    await socket.send_text(world.snapshot().model_dump_json(exclude_none=True))
            await asyncio.sleep(PHYSICS_DT)
        receiver.result()
    except WebSocketDisconnect:
        pass
    finally:
        receiver.cancel()
