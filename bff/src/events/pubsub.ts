import Redis from 'ioredis';
import { config } from '../config';
import { logger } from '../utils/logger';

// Redis channel constants
export const INGESTION_EVENTS_CHANNEL = 'ingestion-events';
export const CACHE_INVALIDATION_CHANNEL = 'cache-invalidation';

// Event type definitions
export interface IngestionEvent {
  type: 'ingestion.pending' | 'ingestion.processing' | 'ingestion.done' | 'ingestion.failed';
  job_id: string;
  document_id: string;
  domain_id: string;
  status: 'pending' | 'processing' | 'done' | 'failed';
  progress: number;
  message: string;
  timestamp: string;
  error?: string;
  user_id?: string;
}

export interface CacheInvalidationEvent {
  type: 'cache.invalidate';
  pattern: string;
  tags?: string[];
  timestamp: string;
}

export type PubSubEvent = IngestionEvent | CacheInvalidationEvent;

// Type guard functions
export function isIngestionEvent(event: PubSubEvent): event is IngestionEvent {
  return event.type.startsWith('ingestion.');
}

export function isCacheInvalidationEvent(event: PubSubEvent): event is CacheInvalidationEvent {
  return event.type === 'cache.invalidate';
}

// Separate Redis connections for pub/sub
// (subscriber can't issue commands while listening)
let subscriber: Redis | null = null;
let publisher: Redis | null = null;

// Track event handlers
const eventHandlers: Map<string, ((event: PubSubEvent) => void)[]> = new Map();

/**
 * Initialize Redis pub/sub connections
 */
export async function initializePubSub(): Promise<void> {
  try {
    // Create subscriber connection
    subscriber = new Redis(config.redisUrl, {
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        logger.warn(`Redis subscriber reconnecting in ${delay}ms (attempt ${times})`);
        return delay;
      },
      maxRetriesPerRequest: null, // Required for pub/sub
    });

    // Create publisher connection
    publisher = new Redis(config.redisUrl, {
      retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
      },
    });

    // Handle subscriber events
    subscriber.on('connect', () => {
      logger.info('Redis pub/sub subscriber connected');
    });

    subscriber.on('error', (err) => {
      logger.error('Redis subscriber error', { error: err.message });
    });

    subscriber.on('message', (channel: string, message: string) => {
      handleIncomingMessage(channel, message);
    });

    // Handle publisher events
    publisher.on('connect', () => {
      logger.info('Redis pub/sub publisher connected');
    });

    publisher.on('error', (err) => {
      logger.error('Redis publisher error', { error: err.message });
    });

    logger.info('Redis pub/sub initialized');
  } catch (error) {
    logger.error('Failed to initialize Redis pub/sub', { error: (error as Error).message });
    throw error;
  }
}

/**
 * Handle incoming Redis message
 */
function handleIncomingMessage(channel: string, message: string): void {
  try {
    const event = JSON.parse(message) as PubSubEvent;
    
    logger.debug('Received pub/sub message', { channel, type: event.type });

    // Get handlers for this channel
    const handlers = eventHandlers.get(channel) || [];
    
    // Call all registered handlers
    handlers.forEach((handler) => {
      try {
        handler(event);
      } catch (handlerError) {
        logger.error('Event handler failed', {
          channel,
          error: (handlerError as Error).message,
        });
      }
    });
  } catch (parseError) {
    logger.error('Failed to parse pub/sub message', {
      channel,
      message: message.substring(0, 200), // Truncate long messages
      error: (parseError as Error).message,
    });
  }
}

/**
 * Subscribe to a Redis channel
 */
export async function subscribeToChannel(
  channel: string,
  handler: (event: PubSubEvent) => void
): Promise<void> {
  if (!subscriber) {
    throw new Error('Pub/sub not initialized. Call initializePubSub() first.');
  }

  try {
    // Subscribe to channel
    await subscriber.subscribe(channel);
    
    // Register handler
    const handlers = eventHandlers.get(channel) || [];
    handlers.push(handler);
    eventHandlers.set(channel, handlers);
    
    logger.info(`Subscribed to channel: ${channel}`);
  } catch (error) {
    logger.error(`Failed to subscribe to channel: ${channel}`, { error: (error as Error).message });
    throw error;
  }
}

/**
 * Unsubscribe from a Redis channel
 */
export async function unsubscribeFromChannel(channel: string): Promise<void> {
  if (!subscriber) {
    return;
  }

  try {
    await subscriber.unsubscribe(channel);
    eventHandlers.delete(channel);
    logger.info(`Unsubscribed from channel: ${channel}`);
  } catch (error) {
    logger.error(`Failed to unsubscribe from channel: ${channel}`, { error: (error as Error).message });
  }
}

/**
 * Publish an event to a Redis channel
 */
export async function publishEvent(channel: string, event: PubSubEvent): Promise<void> {
  if (!publisher) {
    throw new Error('Pub/sub not initialized. Call initializePubSub() first.');
  }

  try {
    const message = JSON.stringify(event);
    await publisher.publish(channel, message);
    
    logger.debug('Published event', { channel, type: event.type });
  } catch (error) {
    logger.error(`Failed to publish event to channel: ${channel}`, { error: (error as Error).message });
    throw error;
  }
}

/**
 * Gracefully shutdown pub/sub connections
 */
export async function shutdownPubSub(): Promise<void> {
  logger.info('Shutting down Redis pub/sub...');
  
  try {
    // Unsubscribe from all channels
    if (subscriber) {
      await subscriber.unsubscribe();
      await subscriber.quit();
      subscriber = null;
    }
    
    // Close publisher
    if (publisher) {
      await publisher.quit();
      publisher = null;
    }
    
    // Clear handlers
    eventHandlers.clear();
    
    logger.info('Redis pub/sub shutdown complete');
  } catch (error) {
    logger.error('Error during pub/sub shutdown', { error: (error as Error).message });
  }
}

/**
 * Get pub/sub health status
 */
export function getPubSubHealth(): { subscriber: string; publisher: string } {
  return {
    subscriber: subscriber?.status || 'disconnected',
    publisher: publisher?.status || 'disconnected',
  };
}

export default {
  initializePubSub,
  subscribeToChannel,
  unsubscribeFromChannel,
  publishEvent,
  shutdownPubSub,
  getPubSubHealth,
  INGESTION_EVENTS_CHANNEL,
  CACHE_INVALIDATION_CHANNEL,
};
