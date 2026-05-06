// Shell services are provided via global window object in Module Federation
// window.__SHELL_BFF_CLIENT__ - BFF API client

declare global {
  interface Window {
    __SHELL_BFF_CLIENT__?: {
      get<T>(path: string): Promise<{ status: number; data?: T; error?: { error: string; message: string } }>
      post<T>(path: string, body: any): Promise<{ status: number; data?: T; error?: { error: string; message: string } }>
      put<T>(path: string, body: any): Promise<{ status: number; data?: T; error?: { error: string; message: string } }>
      delete<T>(path: string): Promise<{ status: number; data?: T; error?: { error: string; message: string } }>
    }
  }
}

declare module 'shell/BaseButton' {
  import { DefineComponent } from 'vue'
  const BaseButton: DefineComponent<any, any, any>
  export default BaseButton
}

declare module 'shell/BaseCard' {
  import { DefineComponent } from 'vue'
  const BaseCard: DefineComponent<any, any, any>
  export default BaseCard
}

declare module 'shell/BaseInput' {
  import { DefineComponent } from 'vue'
  const BaseInput: DefineComponent<any, any, any>
  export default BaseInput
}

declare module 'shell/WebSocketService' {
  import { Ref } from 'vue'
  
  export interface WebSocketService {
    isConnected: Ref<boolean>
    status: Ref<'connecting' | 'connected' | 'disconnected' | 'error'>
    authFailed: Ref<boolean>
    connect(url?: string): void
    disconnect(): void
    on(event: string, callback: (data: any) => void): void
    off(event: string, callback: (data: any) => void): void
    emit(event: string, data: any): void
  }

  export const wsService: WebSocketService
  export const WebSocketKey: symbol
  export function useShellWebSocket(): {
    wsService: WebSocketService
    status: Ref<'connecting' | 'connected' | 'disconnected' | 'error'>
    isConnected: Ref<boolean>
    authFailed: Ref<boolean>
  }
}
