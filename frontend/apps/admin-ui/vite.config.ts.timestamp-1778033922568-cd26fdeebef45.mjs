// vite.config.ts
import { defineConfig } from "file:///D:/02-PERSONAL/01-PROJECTS/25-KnowledgeManagement/frontend/apps/admin-ui/node_modules/vite/dist/node/index.js";
import vue from "file:///D:/02-PERSONAL/01-PROJECTS/25-KnowledgeManagement/frontend/apps/admin-ui/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import federation from "file:///D:/02-PERSONAL/01-PROJECTS/25-KnowledgeManagement/frontend/apps/admin-ui/node_modules/@originjs/vite-plugin-federation/dist/index.mjs";
import { resolve } from "path";
var __vite_injected_original_dirname = "D:\\02-PERSONAL\\01-PROJECTS\\25-KnowledgeManagement\\frontend\\apps\\admin-ui";
var vite_config_default = defineConfig({
  plugins: [
    vue(),
    federation({
      name: "adminUi",
      filename: "remoteEntry.js",
      exposes: { "./App": "./src/App.vue" },
      shared: {
        vue: { singleton: true, requiredVersion: "^3.4.0" },
        pinia: { singleton: true, requiredVersion: "^2.1.0" },
        "vue-router": { singleton: true, requiredVersion: "^4.3.0" }
      }
    })
  ],
  resolve: {
    alias: {
      "shell/microFrontendApi": resolve(__vite_injected_original_dirname, "../shell/src/services/microFrontendApi.ts")
    }
  },
  server: {
    port: 5104,
    strictPort: true,
    origin: "http://localhost:5104",
    cors: {
      origin: ["http://localhost:5100", "http://127.0.0.1:5100"],
      credentials: true
    },
    proxy: {
      "/api": {
        target: "http://localhost:5100",
        changeOrigin: true
      },
      "/auth": {
        target: "http://localhost:5100",
        changeOrigin: true
      }
    }
  },
  preview: {
    port: 5104,
    strictPort: true
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
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFwwMi1QRVJTT05BTFxcXFwwMS1QUk9KRUNUU1xcXFwyNS1Lbm93bGVkZ2VNYW5hZ2VtZW50XFxcXGZyb250ZW5kXFxcXGFwcHNcXFxcYWRtaW4tdWlcIjtjb25zdCBfX3ZpdGVfaW5qZWN0ZWRfb3JpZ2luYWxfZmlsZW5hbWUgPSBcIkQ6XFxcXDAyLVBFUlNPTkFMXFxcXDAxLVBST0pFQ1RTXFxcXDI1LUtub3dsZWRnZU1hbmFnZW1lbnRcXFxcZnJvbnRlbmRcXFxcYXBwc1xcXFxhZG1pbi11aVxcXFx2aXRlLmNvbmZpZy50c1wiO2NvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9pbXBvcnRfbWV0YV91cmwgPSBcImZpbGU6Ly8vRDovMDItUEVSU09OQUwvMDEtUFJPSkVDVFMvMjUtS25vd2xlZGdlTWFuYWdlbWVudC9mcm9udGVuZC9hcHBzL2FkbWluLXVpL3ZpdGUuY29uZmlnLnRzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcbmltcG9ydCB2dWUgZnJvbSAnQHZpdGVqcy9wbHVnaW4tdnVlJ1xuaW1wb3J0IGZlZGVyYXRpb24gZnJvbSAnQG9yaWdpbmpzL3ZpdGUtcGx1Z2luLWZlZGVyYXRpb24nXG5pbXBvcnQgeyByZXNvbHZlIH0gZnJvbSAncGF0aCdcblxuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcbiAgcGx1Z2luczogW1xuICAgIHZ1ZSgpLFxuICAgIGZlZGVyYXRpb24oe1xuICAgICAgbmFtZTogJ2FkbWluVWknLFxuICAgICAgZmlsZW5hbWU6ICdyZW1vdGVFbnRyeS5qcycsXG4gICAgICBleHBvc2VzOiB7ICcuL0FwcCc6ICcuL3NyYy9BcHAudnVlJyB9LFxuICAgICAgc2hhcmVkOiB7XG4gICAgICAgIHZ1ZTogeyBzaW5nbGV0b246IHRydWUsIHJlcXVpcmVkVmVyc2lvbjogJ14zLjQuMCcgfSxcbiAgICAgICAgcGluaWE6IHsgc2luZ2xldG9uOiB0cnVlLCByZXF1aXJlZFZlcnNpb246ICdeMi4xLjAnIH0sXG4gICAgICAgICd2dWUtcm91dGVyJzogeyBzaW5nbGV0b246IHRydWUsIHJlcXVpcmVkVmVyc2lvbjogJ140LjMuMCcgfSxcbiAgICAgIH1cbiAgICB9KVxuICBdLFxuICByZXNvbHZlOiB7XG4gICAgYWxpYXM6IHtcbiAgICAgICdzaGVsbC9taWNyb0Zyb250ZW5kQXBpJzogcmVzb2x2ZShfX2Rpcm5hbWUsICcuLi9zaGVsbC9zcmMvc2VydmljZXMvbWljcm9Gcm9udGVuZEFwaS50cycpLFxuICAgIH1cbiAgfSxcbiAgc2VydmVyOiB7XG4gICAgcG9ydDogNTEwNCxcbiAgICBzdHJpY3RQb3J0OiB0cnVlLFxuICAgIG9yaWdpbjogJ2h0dHA6Ly9sb2NhbGhvc3Q6NTEwNCcsXG4gICAgY29yczoge1xuICAgICAgb3JpZ2luOiBbJ2h0dHA6Ly9sb2NhbGhvc3Q6NTEwMCcsICdodHRwOi8vMTI3LjAuMC4xOjUxMDAnXSxcbiAgICAgIGNyZWRlbnRpYWxzOiB0cnVlLFxuICAgIH0sXG4gICAgcHJveHk6IHtcbiAgICAgICcvYXBpJzoge1xuICAgICAgICB0YXJnZXQ6ICdodHRwOi8vbG9jYWxob3N0OjUxMDAnLFxuICAgICAgICBjaGFuZ2VPcmlnaW46IHRydWUsXG4gICAgICB9LFxuICAgICAgJy9hdXRoJzoge1xuICAgICAgICB0YXJnZXQ6ICdodHRwOi8vbG9jYWxob3N0OjUxMDAnLFxuICAgICAgICBjaGFuZ2VPcmlnaW46IHRydWUsXG4gICAgICB9LFxuICAgIH0sXG4gIH0sXG4gIHByZXZpZXc6IHtcbiAgICBwb3J0OiA1MTA0LFxuICAgIHN0cmljdFBvcnQ6IHRydWUsXG4gIH0sXG4gIGJ1aWxkOiB7IFxuICAgIHRhcmdldDogJ2VzbmV4dCcsXG4gICAgYXNzZXRzRGlyOiAnJyxcbiAgICBtaW5pZnk6IGZhbHNlLFxuICAgIGNzc0NvZGVTcGxpdDogZmFsc2VcbiAgfVxufSkiXSwKICAibWFwcGluZ3MiOiAiO0FBQXdaLFNBQVMsb0JBQW9CO0FBQ3JiLE9BQU8sU0FBUztBQUNoQixPQUFPLGdCQUFnQjtBQUN2QixTQUFTLGVBQWU7QUFIeEIsSUFBTSxtQ0FBbUM7QUFLekMsSUFBTyxzQkFBUSxhQUFhO0FBQUEsRUFDMUIsU0FBUztBQUFBLElBQ1AsSUFBSTtBQUFBLElBQ0osV0FBVztBQUFBLE1BQ1QsTUFBTTtBQUFBLE1BQ04sVUFBVTtBQUFBLE1BQ1YsU0FBUyxFQUFFLFNBQVMsZ0JBQWdCO0FBQUEsTUFDcEMsUUFBUTtBQUFBLFFBQ04sS0FBSyxFQUFFLFdBQVcsTUFBTSxpQkFBaUIsU0FBUztBQUFBLFFBQ2xELE9BQU8sRUFBRSxXQUFXLE1BQU0saUJBQWlCLFNBQVM7QUFBQSxRQUNwRCxjQUFjLEVBQUUsV0FBVyxNQUFNLGlCQUFpQixTQUFTO0FBQUEsTUFDN0Q7QUFBQSxJQUNGLENBQUM7QUFBQSxFQUNIO0FBQUEsRUFDQSxTQUFTO0FBQUEsSUFDUCxPQUFPO0FBQUEsTUFDTCwwQkFBMEIsUUFBUSxrQ0FBVywyQ0FBMkM7QUFBQSxJQUMxRjtBQUFBLEVBQ0Y7QUFBQSxFQUNBLFFBQVE7QUFBQSxJQUNOLE1BQU07QUFBQSxJQUNOLFlBQVk7QUFBQSxJQUNaLFFBQVE7QUFBQSxJQUNSLE1BQU07QUFBQSxNQUNKLFFBQVEsQ0FBQyx5QkFBeUIsdUJBQXVCO0FBQUEsTUFDekQsYUFBYTtBQUFBLElBQ2Y7QUFBQSxJQUNBLE9BQU87QUFBQSxNQUNMLFFBQVE7QUFBQSxRQUNOLFFBQVE7QUFBQSxRQUNSLGNBQWM7QUFBQSxNQUNoQjtBQUFBLE1BQ0EsU0FBUztBQUFBLFFBQ1AsUUFBUTtBQUFBLFFBQ1IsY0FBYztBQUFBLE1BQ2hCO0FBQUEsSUFDRjtBQUFBLEVBQ0Y7QUFBQSxFQUNBLFNBQVM7QUFBQSxJQUNQLE1BQU07QUFBQSxJQUNOLFlBQVk7QUFBQSxFQUNkO0FBQUEsRUFDQSxPQUFPO0FBQUEsSUFDTCxRQUFRO0FBQUEsSUFDUixXQUFXO0FBQUEsSUFDWCxRQUFRO0FBQUEsSUFDUixjQUFjO0FBQUEsRUFDaEI7QUFDRixDQUFDOyIsCiAgIm5hbWVzIjogW10KfQo=
