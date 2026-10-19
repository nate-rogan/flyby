import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  // `npm run dev` forwards API calls to a local uvicorn on :8000
  server: { proxy: { '/api': 'http://localhost:8000' } },
})
