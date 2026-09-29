import { useCallback, useEffect, useRef, useState } from 'react'
import type { ControlMsg, Hello, InputMsg, ServerMsg, State } from './protocol'
import { PROTOCOL_VERSION } from './protocol'

export type Status = 'connecting' | 'open' | 'closed'

/**
 * Collega la UI al server di simulazione.
 * - `hello` arriva una volta (pista, topologia della rete) e finisce nello stato React.
 * - `state` arriva ~30 volte al secondo: va in un ref, letto dal canvas a ogni frame,
 *   così React non ridisegna tutta la pagina 30 volte al secondo.
 */
export function useSimulation() {
  const [status, setStatus] = useState<Status>('connecting')
  const [hello, setHello] = useState<Hello | null>(null)
  const [stats, setStats] = useState<State['stats'] | null>(null)
  const stateRef = useRef<State | null>(null)
  const socketRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    let retry: number | undefined
    let disposed = false

    const connect = () => {
      const proto = location.protocol === 'https:' ? 'wss' : 'ws'
      const ws = new WebSocket(`${proto}://${location.host}/ws`)
      socketRef.current = ws
      setStatus('connecting')
      ws.onopen = () => setStatus('open')
      ws.onmessage = (e) => {
        const msg = JSON.parse(e.data) as ServerMsg
        if (msg.type === 'hello') {
          if (msg.v !== PROTOCOL_VERSION) console.warn('versione protocollo diversa', msg.v)
          setHello(msg)
        } else {
          stateRef.current = msg
          setStats((prev) =>
            prev && prev.mode === msg.stats.mode && prev.alive === msg.stats.alive &&
            prev.generation === msg.stats.generation ? prev : msg.stats,
          )
        }
      }
      ws.onclose = () => {
        setStatus('closed')
        if (!disposed) retry = window.setTimeout(connect, 1000) // il server si riavvia con --reload
      }
    }
    connect()
    return () => {
      disposed = true
      window.clearTimeout(retry)
      socketRef.current?.close()
    }
  }, [])

  const send = useCallback((msg: InputMsg | ControlMsg) => {
    const ws = socketRef.current
    if (ws?.readyState === WebSocket.OPEN) ws.send(JSON.stringify(msg))
  }, [])

  return { status, hello, stats, stateRef, send }
}
