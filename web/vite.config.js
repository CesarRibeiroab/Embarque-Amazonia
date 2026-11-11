import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    // Restrito ao host local para não expor o servidor de desenvolvimento na rede
    host: 'localhost',
  },
});
