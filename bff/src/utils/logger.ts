import winston from 'winston';
import { Request, Response } from 'express';
import { config } from '../config';

const { combine, timestamp, json, printf, colorize } = winston.format;

// Determine log format based on environment
const isDevelopment = config.nodeEnv === 'development';

// Custom format for development (pretty print)
const devFormat = printf(({ level, message, timestamp, service, trace_id, ...metadata }) => {
  const ts = timestamp as string;
  const trId = trace_id ? `[${trace_id}] ` : '';
  const meta = Object.keys(metadata).length ? ` ${JSON.stringify(metadata)}` : '';
  return `${ts} [${service}] ${level}: ${trId}${message}${meta}`;
});

// Create Winston logger instance
export const logger = winston.createLogger({
  level: config.logLevel,
  defaultMeta: {
    service: 'bff',
  },
  format: isDevelopment
    ? combine(
        colorize(),
        timestamp(),
        devFormat
      )
    : combine(
        timestamp(),
        json()
      ),
  transports: [
    new winston.transports.Console(),
  ],
});

// Redact sensitive fields from logs
function redactSensitive(data: Record<string, any>): Record<string, any> {
  const redacted = { ...data };
  const sensitiveFields = ['password', 'token', 'accessToken', 'refreshToken', 'secret', 'authorization'];
  
  for (const field of sensitiveFields) {
    if (field in redacted) {
      redacted[field] = '[REDACTED]';
    }
  }
  
  return redacted;
}

// Log incoming request
export function logRequest(req: Request, res: Response, duration: number): void {
  const trace_id = (req as any).trace_id || 'unknown';
  const user_id = (req as any).user?.id;
  
  logger.info('HTTP request', {
    trace_id,
    user_id,
    method: req.method,
    path: req.path,
    query: req.query,
    status: res.statusCode,
    duration: `${duration}ms`,
    user_agent: req.get('user-agent'),
    ip: req.ip,
  });
}

// Log proxy request
export function logProxyRequest(req: Request, targetPath: string): void {
  const trace_id = (req as any).trace_id || 'unknown';
  const user_id = (req as any).user?.id;
  
  logger.info('Proxy request', {
    trace_id,
    user_id,
    method: req.method,
    path: req.path,
    target: targetPath,
  });
}

// Log proxy response
export function logProxyResponse(req: Request, status: number, duration: number): void {
  const trace_id = (req as any).trace_id || 'unknown';
  
  logger.info('Proxy response', {
    trace_id,
    status,
    duration: `${duration}ms`,
  });
}

// Log errors
export function logError(error: Error, context: Record<string, any> = {}): void {
  logger.error('Error occurred', {
    ...redactSensitive(context),
    error: error.message,
    stack: error.stack,
  });
}

// Log authentication events
export function logAuth(event: string, details: Record<string, any>): void {
  logger.info(`Auth ${event}`, redactSensitive(details));
}

// Log security events
export function logSecurity(event: string, details: Record<string, any>): void {
  logger.warn(`Security ${event}`, redactSensitive(details));
}

// Request logger middleware
export function requestLogger(req: Request, res: Response, next: Function): void {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = Date.now() - start;
    logRequest(req, res, duration);
  });
  
  next();
}

export default logger;
