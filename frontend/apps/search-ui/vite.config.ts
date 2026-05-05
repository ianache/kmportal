import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from '@originjs/vite-plugin-federation'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'searchUi',
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
      'shell/bffClient': resolve(__dirname, '../shell/src/services/bffClient.ts'),
      'shell/BaseButton': resolve(__dirname, '../shell/src/components/ui/BaseButton.vue'),
      'shell/BaseCard': resolve(__dirname, '../shell/src/components/ui/BaseCard.vue'),
      'shell/BaseInput': resolve(__dirname, '../shell/src/components/ui/BaseInput.vue'),
    }
  },
  server: {
    port: 5103,
    strictPort: true,
    origin: 'http://localhost:5103',
  },
  preview: {
    port: 5103,
    strictPort: true,
  },
  build: { 
    target: 'esnext',
    assetsDir: '',
    minify: false,
    cssCodeSplit: false
  }
})