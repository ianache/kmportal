export interface CoreAPIConfig {
  baseUrl: string;
  timeout: number;
}

export interface ProxyOptions {
  target: string;
  changeOrigin: boolean;
  timeout: number;
  pathRewrite?: { [key: string]: string };
  onProxyReq?: (proxyReq: any, req: any, res: any) => void;
  onProxyRes?: (proxyRes: any, req: any, res: any) => void;
  onError?: (err: Error, req: any, res: any) => void;
}

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: APIError;
}

export interface APIError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface ProxyErrorResponse {
  error: string;
  message: string;
  trace_id?: string;
}

export type HTTPStatusCode = 200 | 201 | 400 | 401 | 403 | 404 | 500 | 502 | 504;

export interface ProxyRequestLog {
  method: string;
  path: string;
  target: string;
  trace_id: string;
  user_id?: string;
  timestamp: string;
}

export interface ProxyResponseLog {
  status: number;
  duration: number;
  trace_id: string;
  timestamp: string;
}
