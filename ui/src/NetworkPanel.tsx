import { useEffect, useRef } from 'react'
import type { State } from './protocol'

const INPUT_LABELS = ['↑ −65°', '↑ −20°', '↑ −10°', '↑ 0°', '↑ 10°', '↑ 20°', '↑ 65°', 'VelF']
const OUTPUT_LABELS = ['Steering', 'Acceleration', 'Brake', 'Handbrake']
const POS = '46, 204, 64'    // verde: peso o attivazione positiva
const NEG = '229, 57, 53'    // rosso: negativa
const IDLE = '176, 184, 196' // grigio: dato non ancora disponibile

interface Props {
  layers: number[]
  stateRef: React.RefObject<State | null>
}

/**
 * Il "cervello" visibile, come nel video:
 * - arco verde/rosso = segno del peso, spessore = |peso|
 * - nodo colorato = attivazione corrente
 * Prima della tappa 3 i dati della rete mancano e il grafo resta grigio.
 */
export function NetworkPanel({ layers, stateRef }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current!
    const ctx = canvas.getContext('2d')!
    let raf = 0

    const frame = () => {
      raf = requestAnimationFrame(frame)
      const dpr = window.devicePixelRatio || 1
      const w = canvas.clientWidth, h = canvas.clientHeight
      if (canvas.width !== w * dpr || canvas.height !== h * dpr) {
        canvas.width = w * dpr
        canvas.height = h * dpr
      }
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.clearRect(0, 0, w, h)

      const state = stateRef.current
      const net = state?.network
      // Attivazioni: dalla rete se c'è, altrimenti almeno gli input dai sensori (tappa 2).
      const acts: (number[] | undefined)[] = net?.activations ?? [state?.readings, undefined, state?.outputs]

      const left = 78, right = w - 104, top = 18, bottom = h - (net ? 18 : 34)
      const x = (l: number) => left + (l * (right - left)) / (layers.length - 1)
      const y = (l: number, i: number) =>
        layers[l] === 1 ? (top + bottom) / 2 : top + (i * (bottom - top)) / (layers[l] - 1)

      // Archi
      for (let l = 0; l < layers.length - 1; l++) {
        for (let o = 0; o < layers[l + 1]; o++) {
          for (let i = 0; i < layers[l]; i++) {
            const wgt = net?.weights[l]?.[o]?.[i]
            ctx.strokeStyle = wgt === undefined ? `rgba(${IDLE}, 0.5)` : `rgba(${wgt >= 0 ? POS : NEG}, ${0.25 + Math.min(Math.abs(wgt), 1) * 0.7})`
            ctx.lineWidth = wgt === undefined ? 0.6 : 0.4 + Math.min(Math.abs(wgt), 2) * 1.6
            ctx.beginPath()
            ctx.moveTo(x(l), y(l, i))
            ctx.lineTo(x(l + 1), y(l + 1, o))
            ctx.stroke()
          }
        }
      }

      // Nodi
      for (let l = 0; l < layers.length; l++) {
        for (let i = 0; i < layers[l]; i++) {
          const a = acts[l]?.[i]
          ctx.beginPath()
          ctx.arc(x(l), y(l, i), 7, 0, Math.PI * 2)
          ctx.fillStyle = a === undefined ? '#fff' : `rgba(${a >= 0 ? POS : NEG}, ${0.2 + Math.min(Math.abs(a), 1) * 0.8})`
          ctx.fill()
          ctx.lineWidth = 2
          ctx.strokeStyle = '#3b4250'
          ctx.stroke()
        }
      }

      // Etichette: nomi e valori, come nel video.
      ctx.font = '11px system-ui, sans-serif'
      ctx.fillStyle = '#3b4250'
      const label = (text: string, value: number | undefined, lx: number, ly: number, align: CanvasTextAlign) => {
        ctx.textAlign = align
        ctx.fillText(text, lx, ly - 2)
        ctx.fillStyle = '#7a8291'
        ctx.fillText(value === undefined ? '–' : value.toFixed(2), lx, ly + 10)
        ctx.fillStyle = '#3b4250'
      }
      INPUT_LABELS.slice(0, layers[0]).forEach((t, i) => label(t, acts[0]?.[i], left - 16, y(0, i), 'right'))
      const L = layers.length - 1
      OUTPUT_LABELS.slice(0, layers[L]).forEach((t, i) => label(t, acts[L]?.[i], right + 16, y(L, i), 'left'))

      if (!net) {
        ctx.textAlign = 'center'
        ctx.fillStyle = '#7a8291'
        ctx.fillText('pesi e attivazioni arrivano con la tappa 3', (left + right) / 2, h - 4)
      }
    }
    raf = requestAnimationFrame(frame)
    return () => cancelAnimationFrame(raf)
  }, [layers, stateRef])

  return <canvas ref={canvasRef} className="network-canvas" />
}
