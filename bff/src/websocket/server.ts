import { Server as HttpServer } from 'http';
import { Server as SocketIOServer, Socket } from 'socket.io';
import { config } from '../config';
import { logger } from '../utils/logger';
import { redisClient } from '../middleware/session';
import { UserSession } from '../middleware/session';

// Socket.IO server instance
let io: SocketIOServer | null = null;

// User socket mappings: userId -> Set of socket IDs
const userSocketMap: Map<string, Set<string>> = new Map();

// Socket to user mapping: socketId -> userId
const socketUserMap: Map<string, string> = new Map();

/**
 * Initialize WebSocket server
 */
export function initializeWebSocket(httpServer: HttpServer): SocketIOServer {
  if (io) {
    logger.warn('WebSocket server already initialized');
    return io;
  }

  io = new SocketIOServer(httpServer, {
    path: '/ws',
    cors: {
      origin: config.corsOrigins.length > 0 ? config.corsOrigins : true,
      credentials: true,
      methods: ['GET', 'POST'],
    },
    transports: ['websocket', 'polling'],
    pingTimeout: 60000,
    pingInterval: 25000,
  });

  // Apply authentication middleware
  io.use(socketAuthMiddleware);

  // Handle connections
  io.on('connection', handleConnection);

  logger.info('WebSocket server initialized on path: /ws');
  
  return io;
}

/**
 * Socket authentication middleware
 * Validates session cookie and attaches user info to socket
 */
async function socketAuthMiddleware(socket: Socket, next: (err?: Error) => void): Promise<void> {
  try {
    // Dev bypass — mirror the same bypass logic used by HTTP middleware
    if (process.env.BYPASS_AUTH === 'true') {
      socket.data.user = {
        id: 'dev-user-00000000-0000-0000-0000-000000000000',
        email: 'dev@localhost',
        roles: ['KM_ADMIN'],
      } as UserSession;
      return next();
    }

    // Get session ID from cookie
    const cookie = socket.handshake.headers.cookie;
    if (!cookie) {
      logger.warn('WebSocket connection rejected: no cookie', {
        socketId: socket.id,
      });
      return next(new Error('Authentication required'));
    }

    // Parse session cookie (format: bff.sid=<sessionId>)
    const sessionMatch = cookie.match(/bff\.sid=([^;]+)/);
    if (!sessionMatch) {
      logger.warn('WebSocket connection rejected: no session cookie', {
        socketId: socket.id,
      });
      return next(new Error('Authentication required'));
    }

    const encodedSessionId = sessionMatch[1];
    // URL-decode the session ID (express-session encodes special characters)
    const decodedSessionId = decodeURIComponent(encodedSessionId);
    
    // Parse signed cookie format: s:<sessionId>.<signature>
    // We only need the sessionId part (after 's:' and before the signature)
    let sessionId: string;
    if (decodedSessionId.startsWith('s:')) {
      // Remove 's:' prefix and signature (everything after the first dot)
      const withoutPrefix = decodedSessionId.slice(2);
      const dotIndex = withoutPrefix.indexOf('.');
      sessionId = dotIndex > 0 ? withoutPrefix.slice(0, dotIndex) : withoutPrefix;
    } else {
      sessionId = decodedSessionId;
    }
    
    // Get session from Redis
    const sessionKey = `bff:session:${sessionId}`;
    const sessionData = await redisClient.get(sessionKey);
    
    if (!sessionData) {
      logger.warn('WebSocket connection rejected: invalid session', {
        socketId: socket.id,
        sessionId,
      });
      return next(new Error('Invalid session'));
    }

    // Parse session
    const session = JSON.parse(sessionData);
    const user = session.user as UserSession;
    
    if (!user) {
      logger.warn('WebSocket connection rejected: no user in session', {
        socketId: socket.id,
        sessionId,
      });
      return next(new Error('Not authenticated'));
    }

    // Attach user to socket data
    socket.data.user = user;
    
    logger.info('WebSocket authenticated', {
      socketId: socket.id,
      userId: user.id,
    });
    
    next();
  } catch (error) {
    logger.error('WebSocket authentication error', {
      socketId: socket.id,
      error: (error as Error).message,
    });
    next(new Error('Authentication failed'));
  }
}

/**
 * Handle new WebSocket connection
 */
function handleConnection(socket: Socket): void {
  const user = socket.data.user as UserSession;
  const userId = user.id;
  const socketId = socket.id;
  
  // Register socket mapping
  if (!userSocketMap.has(userId)) {
    userSocketMap.set(userId, new Set());
  }
  userSocketMap.get(userId)!.add(socketId);
  socketUserMap.set(socketId, userId);
  
  logger.info('WebSocket client connected', {
    socketId,
    userId,
    totalConnections: io?.sockets.sockets.size || 0,
  });

  // Emit connected event
  socket.emit('connected', {
    userId: user.id,
    email: user.email,
    roles: user.roles,
    timestamp: new Date().toISOString(),
  });

  // Handle disconnection
  socket.on('disconnect', (reason) => {
    handleDisconnection(socketId, userId, reason);
  });

  // Handle ping/pong for connection health
  socket.on('ping', () => {
    socket.emit('pong', { timestamp: new Date().toISOString() });
  });

  // Handle subscription to rooms
  socket.on('subscribe', (data: { room: string }) => {
    const { room } = data;
    socket.join(room);
    logger.debug(`Socket ${socketId} joined room: ${room}`);
    socket.emit('subscribed', { room });
  });

  socket.on('unsubscribe', (data: { room: string }) => {
    const { room } = data;
    socket.leave(room);
    logger.debug(`Socket ${socketId} left room: ${room}`);
    socket.emit('unsubscribed', { room });
  });
}

/**
 * Handle WebSocket disconnection
 */
function handleDisconnection(socketId: string, userId: string, reason: string): void {
  // Remove socket mappings
  const userSockets = userSocketMap.get(userId);
  if (userSockets) {
    userSockets.delete(socketId);
    if (userSockets.size === 0) {
      userSocketMap.delete(userId);
    }
  }
  socketUserMap.delete(socketId);
  
  logger.info('WebSocket client disconnected', {
    socketId,
    userId,
    reason,
    remainingConnections: io?.sockets.sockets.size || 0,
  });
}

/**
 * Broadcast event to specific user
 */
export function broadcastToUser(userId: string, event: string, data: any): void {
  if (!io) {
    logger.warn('Cannot broadcast: WebSocket server not initialized');
    return;
  }

  const socketIds = userSocketMap.get(userId);
  if (!socketIds || socketIds.size === 0) {
    logger.debug(`No active sockets for user: ${userId}`);
    return;
  }

  socketIds.forEach((socketId) => {
    const socket = io!.sockets.sockets.get(socketId);
    if (socket) {
      socket.emit(event, data);
    }
  });

  logger.debug(`Broadcast to user ${userId}`, { event, socketCount: socketIds.size });
}

/**
 * Broadcast event to all connected clients
 */
export function broadcastToAll(event: string, data: any): void {
  if (!io) {
    logger.warn('Cannot broadcast: WebSocket server not initialized');
    return;
  }

  io.emit(event, data);
  logger.debug('Broadcast to all clients', { event });
}

/**
 * Broadcast event to a specific room
 */
export function broadcastToRoom(room: string, event: string, data: any): void {
  if (!io) {
    logger.warn('Cannot broadcast: WebSocket server not initialized');
    return;
  }

  io.to(room).emit(event, data);
  logger.debug(`Broadcast to room ${room}`, { event });
}

/**
 * Get count of connected users (unique)
 */
export function getConnectedUserCount(): number {
  return userSocketMap.size;
}

/**
 * Get total socket connections
 */
export function getTotalConnections(): number {
  return io?.sockets.sockets.size || 0;
}

/**
 * Get WebSocket health status
 */
export function getWebSocketHealth(): {
  status: string;
  connectedUsers: number;
  totalConnections: number;
} {
  return {
    status: io ? 'initialized' : 'not_initialized',
    connectedUsers: getConnectedUserCount(),
    totalConnections: getTotalConnections(),
  };
}

/**
 * Gracefully shutdown WebSocket server
 */
export async function shutdownWebSocket(): Promise<void> {
  if (!io) {
    return;
  }

  logger.info('Shutting down WebSocket server...');

  // Close all connections
  io.close();
  
  // Clear mappings
  userSocketMap.clear();
  socketUserMap.clear();
  
  io = null;

  logger.info('WebSocket server shutdown complete');
}

export { io };
export default {
  initializeWebSocket,
  broadcastToUser,
  broadcastToAll,
  broadcastToRoom,
  getConnectedUserCount,
  getTotalConnections,
  getWebSocketHealth,
  shutdownWebSocket,
};
