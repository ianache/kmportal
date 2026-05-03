import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from '@originjs/vite-plugin-federation'

export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'ingestionUi',
      filename: 'remoteEntry.js',
      exposes: { './App': './src/App.vue' },
      shared: { vue: { singleton: true, requiredVersion: '^3.4.0' }, pinia: { singleton: true, requiredVersion: '^2.1.0' }, 'vue-router': { singleton: true, requiredVersion: '^4.3.0' } }
    })
  ],
  build: { target: 'esnext' }
})