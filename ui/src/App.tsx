import { useCallback, useState } from 'react'
import { NetworkPanel } from './NetworkPanel'
import type { InputMsg } from './protocol'
import { TrackView } from './TrackView'
import { useKeyboard } from './useKeyboard'
import { useSimulation } from './useSimulation'

const MODE_LABEL = {
  demo: 'demo: auto fantasma (implementa la tappa 1 per guidare)',
  manual: 'guida manuale: frecce o WASD, spazio = freno a mano',
  training: 'addestramento',
  replay: 'replay del campione',
} as const

export default function App() {
  const { status, hello, stats, stateRef, send } = useSimulation()
  const [follow, setFollow] = useState(true)
  const [paused, setPaused] = useState(false)
  const [speed, setSpeed] = useState(1)

  const onInput = useCallback((input: InputMsg) => send(input), [send])
  useKeyboard(onInput)

  const togglePause = () => {
    send({ type: 'control', action: paused ? 'resume' : 'pause' })
    setPaused(!paused)
  }
  const changeSpeed = (value: number) => {
    send({ type: 'control', action: 'speed', value })
    setSpeed(value)
  }

  return (
    <div className="app">
      <header>
        <h1>Neural Network Driving</h1>
        <span className={`status status-${status}`}>
          {status === 'open' ? 'connesso' : status === 'connecting' ? 'connessione…' : 'server non raggiungibile: avvia `make server`'}
        </span>
      </header>

      <main>
        <section className="track">
          {hello ? <TrackView hello={hello} stateRef={stateRef} follow={follow} /> : <div className="placeholder">in attesa della pista…</div>}
        </section>
        <section className="network">
          {hello && <NetworkPanel layers={hello.layers} stateRef={stateRef} />}
        </section>
      </main>

      <footer>
        <span className="mode">{stats ? MODE_LABEL[stats.mode] : '—'}</span>
        <div className="controls">
          <button onClick={togglePause}>{paused ? 'Riprendi' : 'Pausa'}</button>
          <button onClick={() => send({ type: 'control', action: 'reset' })}>Reset</button>
          <button onClick={() => setFollow(!follow)}>{follow ? 'Vista intera' : 'Segui auto'}</button>
          <select value={speed} onChange={(e) => changeSpeed(Number(e.target.value))} aria-label="velocità simulazione">
            {[1, 2, 5, 10].map((v) => <option key={v} value={v}>x{v}</option>)}
          </select>
        </div>
      </footer>
    </div>
  )
}
