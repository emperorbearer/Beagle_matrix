import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';

// dev 서버에서 백엔드(8000)로 API/WebSocket 프록시
export default defineConfig({
  plugins: [svelte()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        ws: true,
      },
    },
  },
});
