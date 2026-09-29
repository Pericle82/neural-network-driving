import { useEffect } from 'react'
import type { InputMsg } from './protocol'

/** Frecce o WASD per guidare, spazio per il freno a mano. Usato dalla modalità "manual". */
export function useKeyboard(onChange: (input: InputMsg) => void) {
  useEffect(() => {
    const down = new Set<string>()
    const emit = () => {
      const left = down.has('ArrowLeft') || down.has('a')
      const right = down.has('ArrowRight') || down.has('d')
      onChange({
        type: 'input',
        steering: (right ? 1 : 0) - (left ? 1 : 0),
        throttle: down.has('ArrowUp') || down.has('w') ? 1 : 0,
        brake: down.has('ArrowDown') || down.has('s') ? 1 : 0,
        handbrake: down.has(' '),
      })
    }
    const onDown = (e: KeyboardEvent) => {
      const k = e.key.length === 1 ? e.key.toLowerCase() : e.key
      if (k.startsWith('Arrow') || k === ' ') e.preventDefault()
      if (!down.has(k)) { down.add(k); emit() }
    }
    const onUp = (e: KeyboardEvent) => {
      down.delete(e.key.length === 1 ? e.key.toLowerCase() : e.key)
      emit()
    }
    window.addEventListener('keydown', onDown)
    window.addEventListener('keyup', onUp)
    return () => {
      window.removeEventListener('keydown', onDown)
      window.removeEventListener('keyup', onUp)
    }
  }, [onChange])
}
