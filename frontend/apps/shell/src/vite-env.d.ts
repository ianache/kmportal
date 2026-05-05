/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_BFF_URL: string
  readonly VITE_WS_URL: string
  readonly VITE_BYPASS_AUTH: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
