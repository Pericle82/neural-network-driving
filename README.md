# Neural Network Driving

> Learn neural networks by building one that drives: a minimal NN (8→6→4) trained with neuroevolution
> in Python/NumPy, visualized live in a React + Canvas UI. Step-by-step course via git tags. Runs fully locally.

Un corso pratico e a tappe: costruisci da zero un'auto che impara a guidare su una pista.
Una rete neurale minima legge 7 raggi-sensore e la velocità, decide sterzo, gas e freni, e
migliora generazione dopo generazione grazie a un algoritmo evolutivo. Una UI nel browser
mostra la pista e, in tempo reale, cosa "pensa" la rete.

```
 ┌────────────── Python ──────────────┐   WebSocket    ┌──────── Browser ────────┐
 │ pista → sensori → rete → comandi   │ ─────────────▶ │ pista, raggi, auto      │
 │   ▲                         │      │   (stato)      │ grafo della rete        │
 │   └──────── fisica ◀────────┘      │ ◀───────────── │ tastiera, pausa, reset  │
 │ evoluzione: sceglie i pesi migliori│   (comandi)    └─────────────────────────┘
 └────────────────────────────────────┘
```

## Avvio rapido

Prerequisiti: `git`, `make`, [uv](https://docs.astral.sh/uv/), Node 20 o superiore.
Su Mac: `brew install uv node`.

```bash
git clone https://github.com/Pericle82/neural-network-driving
cd neural-network-driving
make install
make dev        # apri http://localhost:5173
```

Alla tappa 0 vedi la pista e un'auto "fantasma" che segue la linea centrale: tutto il resto
lo costruisci tu.

## Come funziona il corso

Ogni tappa ha due tag:

- `step-NN-start`: il punto di partenza, con commenti `TODO(step-NN)` che spiegano cosa implementare
  e test che falliscono finché non l'hai fatto. Contiene già la soluzione della tappa precedente.
- `step-NN-solution`: la tappa risolta, da confrontare con la tua versione.

```bash
git checkout step-01-start
make test STEP=1                                   # rossi finché i TODO non sono fatti
make dev                                           # guarda il risultato
git diff step-01-start step-01-solution -- sim/    # la soluzione, se ti blocchi
```

| Tappa | Cosa costruisci | Dove | Cosa vedi alla fine |
| --- | --- | --- | --- |
| 0 | Scheletro, pista, server, UI | tutto | pista e auto fantasma |
| 1 | Fisica dell'auto e collisioni | `sim/car.py` | guidi con la tastiera, i bordi ti eliminano |
| 2 | Sensori a raggio | `sim/sensors.py` | 7 raggi e i loro valori nel pannello |
| 3 | Rete neurale 8→6→4 | `sim/nn.py` | l'auto guida da sola, male; il grafo si colora |
| 4 | Visualizzazione della rete | `ui/src/NetworkPanel.tsx` | archi verdi/rossi, nodi che si accendono |
| 5 | Neuroevoluzione | `sim/evolution.py` | popolazione di auto, fitness che sale |
| 6 | Campione e replay | `server/`, `notebooks/` | il video originale ricreato |
| 7 | Estensioni | libere | reti più profonde, NEAT, PPO |

Disponibili: tappe 0 e 1. Le altre sono in preparazione.

## Struttura

```text
sim/          la simulazione: track.py (fornito), car.py, sensors.py, nn.py, evolution.py
server/       FastAPI + WebSocket: fa girare il mondo e lo trasmette (protocol.py = il contratto)
ui/           Vite + React + Canvas: disegna soltanto
notebooks/    esperimenti in Jupyter, versionati come .py (Jupytext)
tests/        test_stepNN.py: la definizione di "tappa completata"
docs/         protocol.md: i messaggi tra server e UI
```

Regole del progetto:

- **La logica vive in `sim/`**, i notebook la importano e ci sperimentano. Niente stato nascosto nei notebook.
- **Una sola fisica**, in Python. La UI non simula nulla: così l'auto allenata guida uguale ovunque.
- **Caso controllato**: ogni generatore casuale riceve un seed, così test e confronti sono ripetibili.

## Comandi

| Comando | Cosa fa |
| --- | --- |
| `make install` | dipendenze Python (uv) e UI (npm) |
| `make dev` | server di simulazione + UI |
| `make notebook` | JupyterLab sulla cartella `notebooks/` |
| `make test` / `make test STEP=N` | tutti i test / solo quelli della tappa N |

## Per chi mantiene il corso

Le soluzioni complete stanno sul branch `solution`. Ogni parte da far scrivere allo studente
è racchiusa tra `# BEGIN SOLUTION(step-NN) <messaggio>` e `# END SOLUTION` (`//` in TypeScript).
I file `tests/test_stepNN.py` e `notebooks/NN_*.py` compaiono dalla tappa NN in poi.

```bash
git checkout solution
# ...modifica, poi commit...
uv run python tools/make_steps.py          # rigenera step-NN-start/solution e sposta main
git push origin solution
git push --force origin main 'refs/tags/step-*'
```

Un bug corretto su `solution` si propaga così a tutte le tappe. Le date dei commit sono fisse:
se una tappa non cambia, il suo hash resta lo stesso.

## Licenza

MIT
