import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from '@originjs/vite-plugin-federation'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'adminUi',
      filename: 'remoteEntry.js',
      exposes: { './App': './src/App.vue' },
      shared: {
        vue: { singleton: true, requiredVersion: '^3.4.0' },
        pinia: { singleton: true, requiredVersion: '^2.1.0' },
        'vue-router': { singleton: true, requiredVersion: '^4.3.0' },
      }
    })
  ],
  resolve: {
    alias: {
      'shell/microFrontendApi': resolve(__dirname, '../shell/src/services/microFrontendApi.ts'),
    }
  },
  server: {
    port: 5104,
    strictPort: true,
    origin: 'http://localhost:5104',
    cors: {
      origin: ['http://localhost:5100', 'http://127.0.0.1:5100'],
      credentials: true,
    },
    proxy: {
      '/api': {
        target: 'http://localhost:5100',
        changeOrigin: true,
      },
      '/auth': {
        target: 'http://localhost:5100',
        changeOrigin: true,
      },
    },
  },
  preview: {
    port: 5104,
    strictPort: true,
  },
  build: { target: 'esnext' }
})