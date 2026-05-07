import { Request, Response } from 'express';
import { createProxyMiddleware as createHttpProxyMiddleware, Options } from 'http-proxy-middleware';
import { IncomingMessage } from 'http';
import { v4 as uuidv4 } from 'uuid';
import { config } from '../config';
import { refreshAccessToken } from '../auth/keycloak';
import { logProxyRequest, logProxyResponse, logError, logger } from '../utils/logger';

// Track request start times for duration calculation
const requestStartTimes = new Map<string, number>();

// Create proxy middleware factory
export function createProxyMiddleware() {
  const apiUrl = config.apiUrl;
  
  if (!apiUrl) {
    throw new Error('API_URL environment variable is required');
  }

  const proxyOptions: Options = {
    target: apiUrl,
    changeOrigin: true,
    timeout: 30000, // 30 seconds
    proxyTimeout: 30000,
    
    // Path rewriting: /api/v1/* -> /v1/*
    pathRewrite: {
      '^/api': '',
    },
    
    // Modify request before sending to Core API
    on: {
      proxyReq: (proxyReq, incomingReq: IncomingMessage, _res) => {
        const req = incomingReq as any; // Cast to access Express request properties
        const trace_id = req.trace_id || uuidv4();
        const user = req.user;
        
        // Track request start time
        requestStartTimes.set(trace_id, Date.now());
        
        // Add trace ID header
        proxyReq.setHeader('X-Trace-Id', trace_id);
        
        // Add Authorization header with access token
        if (user?.accessToken) {
          proxyReq.setHeader('Authorization', `Bearer ${user.accessToken}`);
        }
        
        // Add user info headers for Core API
        if (user?.id) {
          proxyReq.setHeader('X-User-Id', user.id);
        }
        
        if (user?.email) {
          proxyReq.setHeader('X-User-Email', user.email);
        }
        
        if (user?.roles && user.roles.length > 0) {
          proxyReq.setHeader('X-User-Roles', user.roles.join(','));
        }
        
        // Fix body forwarding: express.json() consumes the body stream before the
        // proxy can pipe it. Re-serialize and write it to the proxy request.
        if (req.body && ['POST', 'PUT', 'PATCH'].includes(req.method || '')) {
          const contentType = req.headers['content-type'] || '';
          
          // Skip for multipart (file uploads) as they are handled by stream piping
          // and express-json doesn't populate req.body for them anyway.
          if (contentType.includes('multipart/form-data')) {
            return;
          }

          let bodyData: string;

          if (contentType.includes('application/json')) {
            bodyData = JSON.stringify(req.body);
          } else if (contentType.includes('application/x-www-form-urlencoded')) {
            bodyData = new URLSearchParams(req.body).toString();
          } else {
            bodyData = JSON.stringify(req.body);
          }

          proxyReq.setHeader('Content-Type', contentType || 'application/json');
          proxyReq.setHeader('Content-Length', Buffer.byteLength(bodyData));
          proxyReq.write(bodyData);
        }
        
        // Log proxy request (redact Authorization header)
        const targetPath = `${apiUrl}${req.url?.replace('/api', '') || req.path || ''}`;
        logProxyRequest(req as Request, targetPath);
        
        logger.debug('Proxy request headers', {
          trace_id,
          path: req.url,
          method: req.method,
          headers: {
            ...req.headers,
            authorization: req.headers?.authorization ? '[REDACTED]' : undefined,
          },
        });
      },
      
      // Handle response from Core API
      proxyRes: async (proxyRes, incomingReq: IncomingMessage, _res) => {
        const req = incomingReq as any;
        const trace_id = req.trace_id || 'unknown';
        const startTime = requestStartTimes.get(trace_id);
        const duration = startTime ? Date.now() - startTime : 0;
        
        // Clean up start time
        requestStartTimes.delete(trace_id);
        
        // Log response
        logProxyResponse(req as Request, proxyRes.statusCode || 0, duration);
        
        // Copy trace ID to response headers
        _res.setHeader('X-Trace-Id', trace_id);

        // Handle token refresh if Core API returns 401
        if (proxyRes.statusCode === 401) {
          await handleProxyResponse(proxyRes, req, _res as Response, () => {});
        }
        
        logger.debug('Proxy response', {
          trace_id,
          status: proxyRes.statusCode,
          duration: `${duration}ms`,
        });
      },
      
      // Handle proxy errors
      error: (err: Error, incomingReq: IncomingMessage, res) => {
        const req = incomingReq as any;
        const trace_id = req.trace_id || 'unknown';
        
        logError(err, {
          trace_id,
          path: req.url,
          message: 'Proxy error occurred',
        });
        
        // Clean up start time if exists
        requestStartTimes.delete(trace_id);
        
        // Send error response if headers not already sent
        const expressRes = res as Response;
        if (!expressRes.headersSent) {
          expressRes.status(502).json({
            error: 'Bad Gateway',
            message: 'Failed to connect to Core API',
            trace_id,
          });
        }
      },
    },
  };

  return createHttpProxyMiddleware(proxyOptions);
}

// Handle 401 responses with token refresh
export async function handleProxyResponse(
  proxyRes: any,
  req: Request,
  _res: Response,
  next: Function
): Promise<void> {
  const trace_id = (req as any).trace_id || 'unknown';
  
  // If Core API returns 401, attempt token refresh
  if (proxyRes.statusCode === 401) {
    const user = (req as any).user;
    
    if (user?.refreshToken) {
      logger.info('Token expired, attempting refresh', { trace_id, user_id: user.id });
      
      try {
        // Refresh the token
        const newTokens = await refreshAccessToken(user.refreshToken);
        
        // Update session with new tokens
        (req.session as any).user = {
          ...user,
          accessToken: newTokens.accessToken,
          refreshToken: newTokens.refreshToken,
          expiresAt: newTokens.expiresAt,
        };
        
        logger.info('Token refreshed successfully', { trace_id, user_id: user.id });
        
        // Note: In a real implementation, you would retry the request
        // For now, we let the 401 pass through and the client should retry
        // A more complete implementation would use a response interceptor
        
      } catch (refreshError) {
        logger.error('Token refresh failed', {
          trace_id,
          user_id: user.id,
          error: (refreshError as Error).message,
        });
        
        // Clear the invalid session
        req.session.destroy((err) => {
          if (err) {
            logger.error('Failed to destroy session', { trace_id, error: err.message });
          }
        });
      }
    }
  }
  
  // Continue with the response
  next();
}

// Error handler for proxy connection failures
export function handleProxyError(err: Error, req: Request, res: Response): void {
  const trace_id = (req as any).trace_id || 'unknown';
  
  logger.error('Core API connection error', {
    trace_id,
    error: err.message,
    path: req.path,
  });
  
  if (!res.headersSent) {
    if ((err as any).code === 'ECONNREFUSED') {
      res.status(502).json({
        error: 'Bad Gateway',
        message: 'Core API is unavailable',
        trace_id,
      });
    } else if ((err as any).code === 'ETIMEDOUT') {
      res.status(504).json({
        error: 'Gateway Timeout',
        message: 'Core API request timed out',
        trace_id,
      });
    } else {
      res.status(502).json({
        error: 'Bad Gateway',
        message: 'Proxy error occurred',
        trace_id,
      });
    }
  }
}

export default createProxyMiddleware;
