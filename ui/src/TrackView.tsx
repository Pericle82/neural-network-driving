import { useEffect, useRef } from 'react'
import type { CarMsg, Hello, Point, State } from './protocol'

// Colori della scena, ispirati al video.
const C = {
  grass: '#6f8196',
  asphalt: '#3f4652',
  border: '#ffffff',
  kerbRed: '#e0403a',
  kerbWhite: '#f4f4f4',
  skid: 'rgba(20, 22, 28, 0.35)',
  ray: 'rgba(255, 255, 255, 0.75)',
  car: '#46b36b',
  carDead: '#9aa1ab',
}
const KERB_CURVATURE = 1 / 170   // sopra questa curvatura (raggio < 170) si disegnano i cordoli
const VIEW_SPAN = 520            // unità del mondo visibili sul lato corto, in modalità "segui"

interface Props {
  hello: Hello
  stateRef: React.RefObject<State | null>
  follow: boolean
}

/**
 * Disegna la pista su un canvas 2D, a ogni frame del browser.
 * Legge lo stato dal ref (aggiornato dal WebSocket) senza passare da React.
 */
export function TrackView({ hello, stateRef, follow }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current!
    const ctx = canvas.getContext('2d')!
    const track = hello.track
    const bounds = boundsOf([...track.left, ...track.right])
    const trail: Point[] = []  // scie delle gomme: ultime posizioni dell'auto seguita
    let raf = 0

    const frame = () => {
      raf = requestAnimationFrame(frame)
      const dpr = window.devicePixelRatio || 1
      const w = canvas.clientWidth, h = canvas.clientHeight
      if (canvas.width !== w * dpr || canvas.height !== h * dpr) {
        canvas.width = w * dpr
        canvas.height = h * dpr
      }
      const state = stateRef.current
      const car = state?.cars.find((c) => c.id === state.focus) ?? state?.cars[0]

      // ── Camera: segue l'auto, oppure inquadra tutta la pista ──
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.fillStyle = C.grass
      ctx.fillRect(0, 0, w, h)
      let scale: number, cx: number, cy: number
      if (follow && car) {
        scale = Math.min(w, h) / VIEW_SPAN
        cx = car.x; cy = car.y
      } else {
        const pad = 30
        scale = Math.min((w - pad * 2) / (bounds.maxX - bounds.minX), (h - pad * 2) / (bounds.maxY - bounds.minY))
        cx = (bounds.minX + bounds.maxX) / 2; cy = (bounds.minY + bounds.maxY) / 2
      }
      ctx.translate(w / 2, h / 2)
      ctx.scale(scale, scale)
      ctx.translate(-cx, -cy)

      drawTrack(ctx, track.left, track.right, track.curvature, scale)

      // ── Scie ──
      if (car?.alive) {
        const last = trail.at(-1)
        if (last && Math.hypot(last[0] - car.x, last[1] - car.y) > 60) trail.length = 0 // ripartenza dal via
        if (!last || Math.hypot(last[0] - car.x, last[1] - car.y) > 3) trail.push([car.x, car.y])
        if (trail.length > 160) trail.shift()
      }
      ctx.strokeStyle = C.skid
      ctx.lineWidth = 2.5
      for (const side of [-5, 5]) {
        ctx.beginPath()
        trail.forEach(([x, y], i) => {
          const next = trail[Math.min(i + 1, trail.length - 1)]
          const a = Math.atan2(next[1] - y, next[0] - x)
          const px = x - Math.sin(a) * side, py = y + Math.cos(a) * side
          if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py)
        })
        ctx.stroke()
      }

      // ── Raggi dei sensori (dalla tappa 2) ──
      if (car && state?.rays) {
        const nose: Point = [car.x + Math.cos(car.heading) * 15, car.y + Math.sin(car.heading) * 15]
        ctx.strokeStyle = C.ray
        ctx.lineWidth = 1 / scale
        for (const [hx, hy] of state.rays) {
          ctx.beginPath()
          ctx.moveTo(nose[0], nose[1])
          ctx.lineTo(hx, hy)
          ctx.stroke()
        }
      }

      // ── Auto ──
      state?.cars.forEach((c) => drawCar(ctx, c, c === car))
    }
    raf = requestAnimationFrame(frame)
    return () => cancelAnimationFrame(raf)
  }, [hello, stateRef, follow])

  return <canvas ref={canvasRef} className="track-canvas" />
}

function boundsOf(points: Point[]) {
  const xs = points.map((p) => p[0]), ys = points.map((p) => p[1])
  return { minX: Math.min(...xs), maxX: Math.max(...xs), minY: Math.min(...ys), maxY: Math.max(...ys) }
}

function drawTrack(ctx: CanvasRenderingContext2D, left: Point[], right: Point[], curvature: number[], scale: number) {
  // Asfalto: l'anello tra i due bordi (regola "evenodd": il buco interno resta vuoto).
  ctx.beginPath()
  for (const border of [left, right]) {
    border.forEach(([x, y], i) => (i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)))
    ctx.closePath()
  }
  ctx.fillStyle = C.asphalt
  ctx.fill('evenodd')

  // Bordi bianchi.
  ctx.strokeStyle = C.border
  ctx.lineWidth = Math.max(2.5, 2 / scale)
  for (const border of [left, right]) {
    ctx.beginPath()
    border.forEach(([x, y], i) => (i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)))
    ctx.closePath()
    ctx.stroke()
  }

  // Cordoli bianco-rossi sul lato interno delle curve strette.
  // Curvatura > 0 = curva a destra (y verso il basso) → interno = bordo destro.
  ctx.lineWidth = 7
  const n = left.length
  for (let i = 0; i < n; i++) {
    const k = curvature[i]
    if (Math.abs(k) < KERB_CURVATURE) continue
    const border = k > 0 ? right : left
    const a = border[i], b = border[(i + 1) % n]
    ctx.strokeStyle = i % 2 === 0 ? C.kerbRed : C.kerbWhite
    ctx.beginPath()
    ctx.moveTo(a[0], a[1])
    ctx.lineTo(b[0], b[1])
    ctx.stroke()
  }
}

function drawCar(ctx: CanvasRenderingContext2D, car: CarMsg, focused: boolean) {
  ctx.save()
  ctx.translate(car.x, car.y)
  ctx.rotate(car.heading)
  ctx.globalAlpha = focused ? 1 : 0.35
  // ruote
  ctx.fillStyle = '#15171c'
  for (const [x, y] of [[9, -8], [9, 5], [-11, -8], [-11, 5]]) ctx.fillRect(x, y, 7, 3)
  // carrozzeria stile monoposto
  ctx.fillStyle = car.alive ? C.car : C.carDead
  ctx.beginPath()
  ctx.roundRect(-15, -5, 30, 10, 3)
  ctx.fill()
  ctx.fillRect(12, -7, 4, 14) // alettone anteriore
  ctx.fillStyle = '#1f2a24'
  ctx.fillRect(-3, -2.5, 7, 5) // abitacolo
  ctx.restore()
}
