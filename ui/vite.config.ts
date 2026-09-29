import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Il browser parla con /ws; Vite inoltra al server di simulazione Python.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/ws': { target: 'ws://localhost:8000', ws: true },
    },
  },
})
