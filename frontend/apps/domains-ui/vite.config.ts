import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'domainsUi',
      filename: 'remoteEntry.js',
      remotes: {
        shell: 'http://localhost:5100/assets/remoteEntry.js',
      },
      exposes: {
        './App': './src/App.vue'
      },
      shared: {
        vue: { singleton: true, requiredVersion: '^3.4.0' },
        pinia: { singleton: true, requiredVersion: '^2.1.0' },
        'vue-router': { singleton: true, requiredVersion: '^4.3.0' },
      }
    })
  ],
  server: {
    port: 5101,
    strictPort: true,
    origin: 'http://localhost:5101',
  },
  preview: {
    port: 5101,
    strictPort: true,
  },
  build: {
    target: 'esnext'
  }
})