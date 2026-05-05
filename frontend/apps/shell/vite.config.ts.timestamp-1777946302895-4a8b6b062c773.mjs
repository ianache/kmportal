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
        domainsUi: "http://localhost:5101/remoteEntry.js",
        searchUi: "http://localhost:5103/remoteEntry.js",
        ingestionUi: "http://localhost:5102/remoteEntry.js",
        adminUi: "http://localhost:5104/remoteEntry.js"
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
    target: "esnext",
    assetsDir: "",
    minify: false,
    cssCodeSplit: false
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFwwMi1QRVJTT05BTFxcXFwwMS1QUk9KRUNUU1xcXFwyNS1Lbm93bGVkZ2VNYW5hZ2VtZW50XFxcXGZyb250ZW5kXFxcXGFwcHNcXFxcc2hlbGxcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIkQ6XFxcXDAyLVBFUlNPTkFMXFxcXDAxLVBST0pFQ1RTXFxcXDI1LUtub3dsZWRnZU1hbmFnZW1lbnRcXFxcZnJvbnRlbmRcXFxcYXBwc1xcXFxzaGVsbFxcXFx2aXRlLmNvbmZpZy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vRDovMDItUEVSU09OQUwvMDEtUFJPSkVDVFMvMjUtS25vd2xlZGdlTWFuYWdlbWVudC9mcm9udGVuZC9hcHBzL3NoZWxsL3ZpdGUuY29uZmlnLnRzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcbmltcG9ydCB2dWUgZnJvbSAnQHZpdGVqcy9wbHVnaW4tdnVlJ1xuaW1wb3J0IGZlZGVyYXRpb24gZnJvbSAnQG9yaWdpbmpzL3ZpdGUtcGx1Z2luLWZlZGVyYXRpb24nXG5cbmV4cG9ydCBkZWZhdWx0IGRlZmluZUNvbmZpZyh7XG4gIHBsdWdpbnM6IFtcbiAgICB2dWUoKSxcbiAgICBmZWRlcmF0aW9uKHtcbiAgICAgIG5hbWU6ICdzaGVsbCcsXG4gICAgICBmaWxlbmFtZTogJ3JlbW90ZUVudHJ5LmpzJyxcbiAgICAgIGV4cG9zZXM6IHtcbiAgICAgICAgJy4vYmZmQ2xpZW50JzogJy4vc3JjL3NlcnZpY2VzL2JmZkNsaWVudC50cycsXG4gICAgICAgICcuL0Jhc2VCdXR0b24nOiAnLi9zcmMvY29tcG9uZW50cy91aS9CYXNlQnV0dG9uLnZ1ZScsXG4gICAgICAgICcuL0Jhc2VDYXJkJzogJy4vc3JjL2NvbXBvbmVudHMvdWkvQmFzZUNhcmQudnVlJyxcbiAgICAgICAgJy4vQmFzZUlucHV0JzogJy4vc3JjL2NvbXBvbmVudHMvdWkvQmFzZUlucHV0LnZ1ZScsXG4gICAgICB9LFxuICAgICAgcmVtb3Rlczoge1xuICAgICAgICBkb21haW5zVWk6ICdodHRwOi8vbG9jYWxob3N0OjUxMDEvcmVtb3RlRW50cnkuanMnLFxuICAgICAgICBzZWFyY2hVaTogJ2h0dHA6Ly9sb2NhbGhvc3Q6NTEwMy9yZW1vdGVFbnRyeS5qcycsXG4gICAgICAgIGluZ2VzdGlvblVpOiAnaHR0cDovL2xvY2FsaG9zdDo1MTAyL3JlbW90ZUVudHJ5LmpzJyxcbiAgICAgICAgYWRtaW5VaTogJ2h0dHA6Ly9sb2NhbGhvc3Q6NTEwNC9yZW1vdGVFbnRyeS5qcycsXG4gICAgICB9LFxuICAgICAgc2hhcmVkOiB7XG4gICAgICAgIHZ1ZTogeyBzaW5nbGV0b246IHRydWUsIGVhZ2VyOiB0cnVlLCByZXF1aXJlZFZlcnNpb246ICdeMy40LjAnIH0sXG4gICAgICAgIHBpbmlhOiB7IHNpbmdsZXRvbjogdHJ1ZSwgZWFnZXI6IHRydWUsIHJlcXVpcmVkVmVyc2lvbjogJ14yLjEuMCcgfSxcbiAgICAgICAgJ3Z1ZS1yb3V0ZXInOiB7IHNpbmdsZXRvbjogdHJ1ZSwgZWFnZXI6IHRydWUsIHJlcXVpcmVkVmVyc2lvbjogJ140LjMuMCcgfSxcbiAgICAgIH1cbiAgICB9KVxuICBdLFxuICBzZXJ2ZXI6IHtcbiAgICBwb3J0OiA1MTAwLFxuICAgIHN0cmljdFBvcnQ6IHRydWUsXG4gICAgcHJveHk6IHtcbiAgICAgICcvYXBpJzogJ2h0dHA6Ly9sb2NhbGhvc3Q6MzAwMCcsXG4gICAgICAnL2F1dGgnOiAnaHR0cDovL2xvY2FsaG9zdDozMDAwJyxcbiAgICB9LFxuICB9LFxuICBidWlsZDoge1xuICAgIHRhcmdldDogJ2VzbmV4dCcsXG4gICAgYXNzZXRzRGlyOiAnJyxcbiAgICBtaW5pZnk6IGZhbHNlLFxuICAgIGNzc0NvZGVTcGxpdDogZmFsc2VcbiAgfVxufSkiXSwKICAibWFwcGluZ3MiOiAiO0FBQStZLFNBQVMsb0JBQW9CO0FBQzVhLE9BQU8sU0FBUztBQUNoQixPQUFPLGdCQUFnQjtBQUV2QixJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUMxQixTQUFTO0FBQUEsSUFDUCxJQUFJO0FBQUEsSUFDSixXQUFXO0FBQUEsTUFDVCxNQUFNO0FBQUEsTUFDTixVQUFVO0FBQUEsTUFDVixTQUFTO0FBQUEsUUFDUCxlQUFlO0FBQUEsUUFDZixnQkFBZ0I7QUFBQSxRQUNoQixjQUFjO0FBQUEsUUFDZCxlQUFlO0FBQUEsTUFDakI7QUFBQSxNQUNBLFNBQVM7QUFBQSxRQUNQLFdBQVc7QUFBQSxRQUNYLFVBQVU7QUFBQSxRQUNWLGFBQWE7QUFBQSxRQUNiLFNBQVM7QUFBQSxNQUNYO0FBQUEsTUFDQSxRQUFRO0FBQUEsUUFDTixLQUFLLEVBQUUsV0FBVyxNQUFNLE9BQU8sTUFBTSxpQkFBaUIsU0FBUztBQUFBLFFBQy9ELE9BQU8sRUFBRSxXQUFXLE1BQU0sT0FBTyxNQUFNLGlCQUFpQixTQUFTO0FBQUEsUUFDakUsY0FBYyxFQUFFLFdBQVcsTUFBTSxPQUFPLE1BQU0saUJBQWlCLFNBQVM7QUFBQSxNQUMxRTtBQUFBLElBQ0YsQ0FBQztBQUFBLEVBQ0g7QUFBQSxFQUNBLFFBQVE7QUFBQSxJQUNOLE1BQU07QUFBQSxJQUNOLFlBQVk7QUFBQSxJQUNaLE9BQU87QUFBQSxNQUNMLFFBQVE7QUFBQSxNQUNSLFNBQVM7QUFBQSxJQUNYO0FBQUEsRUFDRjtBQUFBLEVBQ0EsT0FBTztBQUFBLElBQ0wsUUFBUTtBQUFBLElBQ1IsV0FBVztBQUFBLElBQ1gsUUFBUTtBQUFBLElBQ1IsY0FBYztBQUFBLEVBQ2hCO0FBQ0YsQ0FBQzsiLAogICJuYW1lcyI6IFtdCn0K
