# UI

Vite + React + TypeScript + Canvas 2D. La UI **disegna soltanto**: tutta la logica (fisica, sensori,
rete, evoluzione) sta nel server Python e arriva via WebSocket (vedi [../docs/protocol.md](../docs/protocol.md)).

| File | Ruolo |
| --- | --- |
| `src/protocol.ts` | tipi dei messaggi, specchio di `server/protocol.py` |
| `src/useSimulation.ts` | connessione WebSocket, riconnessione automatica |
| `src/useKeyboard.ts` | frecce/WASD + spazio → messaggio `input` |
| `src/TrackView.tsx` | pista, cordoli, scie, raggi, auto (camera che segue o vista intera) |
| `src/NetworkPanel.tsx` | il grafo della rete: archi verdi/rossi, nodi colorati per attivazione |

Avvio dalla radice del repo: `make ui` (oppure `make dev` per server + UI).
