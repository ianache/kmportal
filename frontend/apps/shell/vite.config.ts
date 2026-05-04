import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'shell',
      remotes: {
        domainsUi: 'http://localhost:5101/assets/remoteEntry.js',
        searchUi: 'http://localhost:5103/assets/remoteEntry.js',
        ingestionUi: 'http://localhost:5102/assets/remoteEntry.js',
        adminUi: 'http://localhost:5104/assets/remoteEntry.js',
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
    proxy: {
      '/api': 'http://localhost:3000',
      '/auth': 'http://localhost:3000',
    },
  },
  build: {
    target: 'esnext'
  }
})