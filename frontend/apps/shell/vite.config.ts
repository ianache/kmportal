import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'shell',
      remotes: {
        domainsUi: 'http://localhost:5101/remoteEntry.js',
        searchUi: 'http://localhost:5103/remoteEntry.js',
        ingestionUi: 'http://localhost:5102/remoteEntry.js',
        adminUi: 'http://localhost:5104/remoteEntry.js',
      },
      shared: {
        vue: { singleton: true, eager: true, requiredVersion: '^3.4.0' },
        pinia: { singleton: true, eager: true, requiredVersion: '^2.1.0' },
        'vue-router': { singleton: true, eager: true, requiredVersion: '^4.3.0' },
      }
    })
  ],
  server: {
    port: 5100,
    strictPort: true,
    origin: 'http://localhost:5100',
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
      '/auth/login': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
      '/auth/logout': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
      '/auth/session': {
        target: 'http://localhost:3000',
        changeOrigin: true,
      },
      '/ws': {
        target: 'http://localhost:3000',
        ws: true,
        changeOrigin: true,
        // Suppress noisy ECONNRESET logs when the BFF WS server is not yet ready
        // or when the browser closes the connection on navigation.
        configure: (proxy) => {
          proxy.on('error', (err: NodeJS.ErrnoException) => {
            if (err.code !== 'ECONNRESET') console.error('[ws proxy]', err.message);
          });
        },
      },

    },
  },
  preview: {
    port: 5100,
    strictPort: true,
  },
  build: {
    target: 'esnext',
    assetsDir: '',
    minify: false,
    cssCodeSplit: false
  }
})