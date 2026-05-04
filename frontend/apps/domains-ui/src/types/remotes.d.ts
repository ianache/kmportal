declare module 'shell/bffClient' {
  export interface ApiError {
    error: string
    message: string
    trace_id?: string
  }

  export interface ApiResponse<T> {
    data?: T
    error?: ApiError
    status: number
  }

  export interface BffClient {
    get<T>(path: string, options?: RequestInit): Promise<ApiResponse<T>>
    post<T>(path: string, body: any, options?: RequestInit): Promise<ApiResponse<T>>
    put<T>(path: string, body: any, options?: RequestInit): Promise<ApiResponse<T>>
    delete<T>(path: string, options?: RequestInit): Promise<ApiResponse<T>>
  }

  export const bffClient: BffClient
  export default bffClient
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
