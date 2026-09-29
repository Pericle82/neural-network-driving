// Specchio TypeScript di server/protocol.py. Se cambi uno, cambia l'altro
// (e docs/protocol.md): è il contratto tra simulazione e UI.

export const PROTOCOL_VERSION = 1

export type Point = [number, number]

export interface TrackMsg {
  center: Point[]
  left: Point[]
  right: Point[]
  curvature: number[]
  width: number
}

export interface Hello {
  type: 'hello'
  v: number
  track: TrackMsg
  layers: number[]
}

export interface CarMsg {
  id: number
  x: number
  y: number
  heading: number
  speed: number
  alive: boolean
}

export interface NetworkMsg {
  weights: number[][][]
  activations: number[][]
}

export interface Stats {
  mode: 'demo' | 'manual' | 'training' | 'replay'
  generation: number
  alive: number
  best_fitness: number
}

export interface State {
  type: 'state'
  t: number
  cars: CarMsg[]
  focus?: number
  rays?: Point[]
  readings?: number[]
  outputs?: number[]
  network?: NetworkMsg
  stats: Stats
}

export type ServerMsg = Hello | State

export interface InputMsg {
  type: 'input'
  steering: number
  throttle: number
  brake: number
  handbrake: boolean
}

export interface ControlMsg {
  type: 'control'
  action: 'pause' | 'resume' | 'reset' | 'speed'
  value?: number
}
