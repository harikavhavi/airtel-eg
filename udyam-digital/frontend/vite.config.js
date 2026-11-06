import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/advisor': 'http://localhost:8000',
      '/quote':   'http://localhost:8000',
      '/kyc':     'http://localhost:8000',
      '/tracker': 'http://localhost:8000',
      '/propensity': 'http://localhost:8000',
    },
  },
})

