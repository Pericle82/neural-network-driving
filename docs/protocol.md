# Protocollo WebSocket (v1)

Il server di simulazione (Python) e la UI (browser) si parlano su un'unica WebSocket, `ws://localhost:8000/ws`
(in sviluppo la UI la raggiunge come `/ws` tramite il proxy di Vite). Tutti i messaggi sono JSON con un campo `type`.

Fonte di verità: [`server/protocol.py`](../server/protocol.py); specchio TypeScript: [`ui/src/protocol.ts`](../ui/src/protocol.ts).
Se cambi un messaggio, aggiorna i due file e questa pagina, e incrementa `v` se la modifica non è retrocompatibile.

```
browser                         server
   │ ───────── connessione ────────▶ │
   │ ◀──────── hello (1 volta) ───── │  pista + topologia della rete
   │ ◀──────── state (~30/s) ─────── │  auto, raggi, rete, statistiche
   │ ───────── input ──────────────▶ │  comandi da tastiera (modalità manual)
   │ ───────── control ────────────▶ │  pausa, reset, velocità
```

## Server → browser

### `hello`
| Campo | Tipo | Significato |
| --- | --- | --- |
| `v` | int | versione del protocollo (1) |
| `track.center`, `track.left`, `track.right` | `[x, y][]` | linea centrale e bordi, stessi indici |
| `track.curvature` | `number[]` | curvatura con segno per punto (> 0 = curva a destra); la UI la usa per i cordoli |
| `track.width` | number | larghezza della pista |
| `layers` | `int[]` | topologia della rete, per esempio `[8, 6, 4]` |

### `state`
| Campo | Tipo | Da quale tappa | Significato |
| --- | --- | --- | --- |
| `t` | number | 0 | tempo simulato (s) |
| `cars[]` | `{id, x, y, heading, speed, alive}` | 0 | tutte le auto (una sola fino alla tappa 5) |
| `focus` | int | 0 | id dell'auto seguita dalla camera |
| `rays` | `[x, y][]` | 2 | punti d'impatto dei 7 raggi dell'auto seguita |
| `readings` | `number[8]` | 2 | input della rete: 7 raggi + velocità, in [0, 1] |
| `outputs` | `number[4]` | 3 | sterzo, gas, freno, freno a mano |
| `network.weights` | `number[][][]` | 3 | una matrice `(n_out, n_in)` per strato |
| `network.activations` | `number[][]` | 3 | un vettore per strato, input compreso |
| `stats` | `{mode, generation, alive, best_fitness}` | 0 | `mode`: `demo`, `manual`, `training`, `replay` |

I campi non ancora disponibili vengono omessi.

## Browser → server

### `input`
`{ "type": "input", "steering": -1..1, "throttle": 0..1, "brake": 0..1, "handbrake": bool }`

### `control`
`{ "type": "control", "action": "pause" | "resume" | "reset" | "speed", "value"?: number }`, con `value` = moltiplicatore di velocità per `speed` (da 0.25 a 100).
