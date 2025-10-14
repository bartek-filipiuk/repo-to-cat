// @ts-check
import { defineConfig } from 'astro/config';
import node from '@astrojs/node';
import tailwind from '@astrojs/tailwind';

// https://astro.build/config
export default defineConfig({
  output: 'server',  // Enable SSR
  adapter: node({
    mode: 'standalone'
  }),
  integrations: [tailwind()],
  server: {
    port: 4321,
    host: true
  },
  // API proxy (optional, for development)
  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    }
  }
});
