import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import federation from '@originjs/vite-plugin-federation'
import { resolve } from 'path'

export default defineConfig({
  plugins: [
    vue(),
    federation({
      name: 'domainsUi',
      filename: 'remoteEntry.js',
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
  resolve: {
    alias: [
      // Exact-match alias: bypass exports-field resolution for vite-plugin-federation compat.
      // Regex ensures @vue-flow/core/dist/style.css subpaths are NOT affected.
      {
        find: /^@vue-flow\/core$/,
        replacement: resolve(__dirname, 'node_modules/@vue-flow/core/dist/vue-flow-core.mjs'),
      },
      { find: 'shell/microFrontendApi', replacement: resolve(__dirname, '../shell/src/services/microFrontendApi.ts') },
      { find: 'shell/authStore',        replacement: resolve(__dirname, '../shell/src/stores/auth.ts') },
      { find: 'shell/BaseButton',       replacement: resolve(__dirname, '../shell/src/components/ui/BaseButton.vue') },
      { find: 'shell/BaseCard',         replacement: resolve(__dirname, '../shell/src/components/ui/BaseCard.vue') },
      { find: 'shell/BaseInput',        replacement: resolve(__dirname, '../shell/src/components/ui/BaseInput.vue') },
    ]
  },
  optimizeDeps: {
    include: ['@vue-flow/core'],
  },
  server: {
    port: 5101,
    strictPort: true,
    origin: 'http://localhost:5101',
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
    port: 5101,
    strictPort: true,
  },
  build: {
    target: 'esnext',
    assetsDir: '',
    minify: false,
    cssCodeSplit: false,
  }
})
