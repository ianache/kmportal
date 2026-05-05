// vite.config.ts
import { defineConfig } from "file:///D:/02-PERSONAL/01-PROJECTS/25-KnowledgeManagement/frontend/apps/shell/node_modules/vite/dist/node/index.js";
import vue from "file:///D:/02-PERSONAL/01-PROJECTS/25-KnowledgeManagement/frontend/apps/shell/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import federation from "file:///D:/02-PERSONAL/01-PROJECTS/25-KnowledgeManagement/frontend/apps/shell/node_modules/@originjs/vite-plugin-federation/dist/index.mjs";
var vite_config_default = defineConfig({
  plugins: [
    vue(),
    federation({
      name: "shell",
      filename: "remoteEntry.js",
      exposes: {
        "./bffClient": "./src/services/bffClient.ts",
        "./BaseButton": "./src/components/ui/BaseButton.vue",
        "./BaseCard": "./src/components/ui/BaseCard.vue",
        "./BaseInput": "./src/components/ui/BaseInput.vue"
      },
      remotes: {
        domainsUi: "http://localhost:5101/assets/remoteEntry.js",
        searchUi: "http://localhost:5103/assets/remoteEntry.js",
        ingestionUi: "http://localhost:5102/assets/remoteEntry.js",
        adminUi: "http://localhost:5104/assets/remoteEntry.js"
      },
      shared: {
        vue: { singleton: true, eager: true, requiredVersion: "^3.4.0" },
        pinia: { singleton: true, eager: true, requiredVersion: "^2.1.0" },
        "vue-router": { singleton: true, eager: true, requiredVersion: "^4.3.0" }
      }
    })
  ],
  server: {
    port: 5100,
    strictPort: true,
    proxy: {
      "/api": "http://localhost:3000",
      "/auth": "http://localhost:3000"
    }
  },
  build: {
    target: "esnext"
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFwwMi1QRVJTT05BTFxcXFwwMS1QUk9KRUNUU1xcXFwyNS1Lbm93bGVkZ2VNYW5hZ2VtZW50XFxcXGZyb250ZW5kXFxcXGFwcHNcXFxcc2hlbGxcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIkQ6XFxcXDAyLVBFUlNPTkFMXFxcXDAxLVBST0pFQ1RTXFxcXDI1LUtub3dsZWRnZU1hbmFnZW1lbnRcXFxcZnJvbnRlbmRcXFxcYXBwc1xcXFxzaGVsbFxcXFx2aXRlLmNvbmZpZy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vRDovMDItUEVSU09OQUwvMDEtUFJPSkVDVFMvMjUtS25vd2xlZGdlTWFuYWdlbWVudC9mcm9udGVuZC9hcHBzL3NoZWxsL3ZpdGUuY29uZmlnLnRzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcbmltcG9ydCB2dWUgZnJvbSAnQHZpdGVqcy9wbHVnaW4tdnVlJ1xuaW1wb3J0IGZlZGVyYXRpb24gZnJvbSAnQG9yaWdpbmpzL3ZpdGUtcGx1Z2luLWZlZGVyYXRpb24nXG5cbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XG4gIHBsdWdpbnM6IFtcbiAgICB2dWUoKSxcbiAgICBmZWRlcmF0aW9uKHtcbiAgICAgIG5hbWU6ICdzaGVsbCcsXG4gICAgICBmaWxlbmFtZTogJ3JlbW90ZUVudHJ5LmpzJyxcbiAgICAgIGV4cG9zZXM6IHtcbiAgICAgICAgJy4vYmZmQ2xpZW50JzogJy4vc3JjL3NlcnZpY2VzL2JmZkNsaWVudC50cycsXG4gICAgICAgICcuL0Jhc2VCdXR0b24nOiAnLi9zcmMvY29tcG9uZW50cy91aS9CYXNlQnV0dG9uLnZ1ZScsXG4gICAgICAgICcuL0Jhc2VDYXJkJzogJy4vc3JjL2NvbXBvbmVudHMvdWkvQmFzZUNhcmQudnVlJyxcbiAgICAgICAgJy4vQmFzZUlucHV0JzogJy4vc3JjL2NvbXBvbmVudHMvdWkvQmFzZUlucHV0LnZ1ZScsXG4gICAgICB9LFxuICAgICAgcmVtb3Rlczoge1xuICAgICAgICBkb21haW5zVWk6ICdodHRwOi8vbG9jYWxob3N0OjUxMDEvYXNzZXRzL3JlbW90ZUVudHJ5LmpzJyxcbiAgICAgICAgc2VhcmNoVWk6ICdodHRwOi8vbG9jYWxob3N0OjUxMDMvYXNzZXRzL3JlbW90ZUVudHJ5LmpzJyxcbiAgICAgICAgaW5nZXN0aW9uVWk6ICdodHRwOi8vbG9jYWxob3N0OjUxMDIvYXNzZXRzL3JlbW90ZUVudHJ5LmpzJyxcbiAgICAgICAgYWRtaW5VaTogJ2h0dHA6Ly9sb2NhbGhvc3Q6NTEwNC9hc3NldHMvcmVtb3RlRW50cnkuanMnLFxuICAgICAgfSxcbiAgICAgIHNoYXJlZDoge1xuICAgICAgICB2dWU6IHsgc2luZ2xldG9uOiB0cnVlLCBlYWdlcjogdHJ1ZSwgcmVxdWlyZWRWZXJzaW9uOiAnXjMuNC4wJyB9LFxuICAgICAgICBwaW5pYTogeyBzaW5nbGV0b246IHRydWUsIGVhZ2VyOiB0cnVlLCByZXF1aXJlZFZlcnNpb246ICdeMi4xLjAnIH0sXG4gICAgICAgICd2dWUtcm91dGVyJzogeyBzaW5nbGV0b246IHRydWUsIGVhZ2VyOiB0cnVlLCByZXF1aXJlZFZlcnNpb246ICdeNC4zLjAnIH0sXG4gICAgICB9XG4gICAgfSlcbiAgXSxcbiAgc2VydmVyOiB7XG4gICAgcG9ydDogNTEwMCxcbiAgICBzdHJpY3RQb3J0OiB0cnVlLFxuICAgIHByb3h5OiB7XG4gICAgICAnL2FwaSc6ICdodHRwOi8vbG9jYWxob3N0OjMwMDAnLFxuICAgICAgJy9hdXRoJzogJ2h0dHA6Ly9sb2NhbGhvc3Q6MzAwMCcsXG4gICAgfSxcbiAgfSxcbiAgYnVpbGQ6IHtcbiAgICB0YXJnZXQ6ICdlc25leHQnXG4gIH1cbn0pIl0sCiAgIm1hcHBpbmdzIjogIjtBQUErWSxTQUFTLG9CQUFvQjtBQUM1YSxPQUFPLFNBQVM7QUFDaEIsT0FBTyxnQkFBZ0I7QUFFdkIsSUFBTyxzQkFBUSxhQUFhO0FBQUEsRUFDMUIsU0FBUztBQUFBLElBQ1AsSUFBSTtBQUFBLElBQ0osV0FBVztBQUFBLE1BQ1QsTUFBTTtBQUFBLE1BQ04sVUFBVTtBQUFBLE1BQ1YsU0FBUztBQUFBLFFBQ1AsZUFBZTtBQUFBLFFBQ2YsZ0JBQWdCO0FBQUEsUUFDaEIsY0FBYztBQUFBLFFBQ2QsZUFBZTtBQUFBLE1BQ2pCO0FBQUEsTUFDQSxTQUFTO0FBQUEsUUFDUCxXQUFXO0FBQUEsUUFDWCxVQUFVO0FBQUEsUUFDVixhQUFhO0FBQUEsUUFDYixTQUFTO0FBQUEsTUFDWDtBQUFBLE1BQ0EsUUFBUTtBQUFBLFFBQ04sS0FBSyxFQUFFLFdBQVcsTUFBTSxPQUFPLE1BQU0saUJBQWlCLFNBQVM7QUFBQSxRQUMvRCxPQUFPLEVBQUUsV0FBVyxNQUFNLE9BQU8sTUFBTSxpQkFBaUIsU0FBUztBQUFBLFFBQ2pFLGNBQWMsRUFBRSxXQUFXLE1BQU0sT0FBTyxNQUFNLGlCQUFpQixTQUFTO0FBQUEsTUFDMUU7QUFBQSxJQUNGLENBQUM7QUFBQSxFQUNIO0FBQUEsRUFDQSxRQUFRO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixZQUFZO0FBQUEsSUFDWixPQUFPO0FBQUEsTUFDTCxRQUFRO0FBQUEsTUFDUixTQUFTO0FBQUEsSUFDWDtBQUFBLEVBQ0Y7QUFBQSxFQUNBLE9BQU87QUFBQSxJQUNMLFFBQVE7QUFBQSxFQUNWO0FBQ0YsQ0FBQzsiLAogICJuYW1lcyI6IFtdCn0K
