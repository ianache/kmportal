import { 
  subscribeToChannel, 
  INGESTION_EVENTS_CHANNEL, 
  IngestionEvent, 
  isIngestionEvent,
  PubSubEvent 
} from '../../events/pubsub';
import { broadcastToUser, broadcastToRoom } from '../server';
import { logger } from '../../utils/logger';

/**
 * Initialize ingestion event handlers
 * Subscribes to Redis pub/sub and broadcasts to WebSocket clients
 */
export async function initializeIngestionHandlers(): Promise<void> {
  logger.info('Initializing ingestion event handlers...');
  
  try {
    // Subscribe to ingestion events channel
    await subscribeToChannel(INGESTION_EVENTS_CHANNEL, handleIngestionEvent);
    
    logger.info('Ingestion event handlers initialized');
  } catch (error) {
    logger.error('Failed to initialize ingestion handlers', { error: (error as Error).message });
    throw error;
  }
}

/**
 * Handle ingestion event from Redis pub/sub
 */
function handleIngestionEvent(event: PubSubEvent): void {
  // Validate event type
  if (!isIngestionEvent(event)) {
    logger.warn('Received non-ingestion event on ingestion channel', { type: event.type });
    return;
  }

  // Log event
  logger.info('Processing ingestion event', {
    type: event.type,
    job_id: event.job_id,
    document_id: event.document_id,
    domain_id: event.domain_id,
    status: event.status,
    progress: event.progress,
  });

  // Handle the event
  handleJobUpdate(event);
}

/**
 * Handle job status update
 * Determines target users and broadcasts event
 */
export function handleJobUpdate(event: IngestionEvent): void {
  const { user_id, domain_id, job_id } = event;

  // Broadcast to the user who submitted the job (if known)
  if (user_id) {
    broadcastToUser(user_id, 'ingestion:update', {
      jobId: job_id,
      documentId: event.document_id,
      domainId: domain_id,
      status: event.status,
      progress: event.progress,
      message: event.message,
      timestamp: event.timestamp,
      error: event.error,
    });
  }

  // Broadcast to domain room (all users with access to this domain)
  const domainRoom = `domain:${domain_id}`;
  broadcastToRoom(domainRoom, 'ingestion:update', {
    jobId: job_id,
    documentId: event.document_id,
    domainId: domain_id,
    status: event.status,
    progress: event.progress,
    message: event.message,
    timestamp: event.timestamp,
    error: event.error,
  });

  // Handle specific status transitions
  switch (event.status) {
    case 'done':
      handleJobComplete(event);
      break;
    case 'failed':
      handleJobFailed(event);
      break;
    case 'processing':
      handleJobProcessing(event);
      break;
    case 'pending':
      handleJobPending(event);
      break;
  }
}

/**
 * Handle job pending status
 */
function handleJobPending(event: IngestionEvent): void {
  logger.debug('Job pending', { job_id: event.job_id });
  
  // Could emit specific event or just use the general update
  broadcastJobEvent(event, 'ingestion:pending');
}

/**
 * Handle job processing status
 */
function handleJobProcessing(event: IngestionEvent): void {
  logger.debug('Job processing', { 
    job_id: event.job_id, 
    progress: event.progress 
  });
  
  // Broadcast progress update
  broadcastJobEvent(event, 'ingestion:processing');
}

/**
 * Handle job completion
 */
function handleJobComplete(event: IngestionEvent): void {
  logger.info('Job completed', { 
    job_id: event.job_id,
    document_id: event.document_id,
  });
  
  // Broadcast completion event
  broadcastJobEvent(event, 'ingestion:complete');
}

/**
 * Handle job failure
 */
function handleJobFailed(event: IngestionEvent): void {
  logger.warn('Job failed', { 
    job_id: event.job_id,
    document_id: event.document_id,
    error: event.error,
  });
  
  // Broadcast failure event
  broadcastJobEvent(event, 'ingestion:error');
}

/**
 * Broadcast job event to relevant clients
 */
function broadcastJobEvent(event: IngestionEvent, eventName: string): void {
  const payload = {
    jobId: event.job_id,
    documentId: event.document_id,
    domainId: event.domain_id,
    status: event.status,
    progress: event.progress,
    message: event.message,
    timestamp: event.timestamp,
    error: event.error,
  };

  // Broadcast to user if known
  if (event.user_id) {
    broadcastToUser(event.user_id, eventName, payload);
  }

  // Broadcast to domain room
  const domainRoom = `domain:${event.domain_id}`;
  broadcastToRoom(domainRoom, eventName, payload);
}

/**
 * Broadcast ingestion event manually (for testing or external triggers)
 */
export function broadcastIngestionEvent(event: IngestionEvent): void {
  handleJobUpdate(event);
}

/**
 * Validate ingestion event schema
 */
export function validateIngestionEvent(event: any): event is IngestionEvent {
  if (!event || typeof event !== 'object') {
    return false;
  }

  const required = ['type', 'job_id', 'document_id', 'domain_id', 'status', 'progress', 'message', 'timestamp'];
  
  for (const field of required) {
    if (!(field in event)) {
      logger.warn('Ingestion event missing required field', { field, event });
      return false;
    }
  }

  // Validate status values
  const validStatuses = ['pending', 'processing', 'done', 'failed'];
  if (!validStatuses.includes(event.status)) {
    logger.warn('Invalid status in ingestion event', { status: event.status });
    return false;
  }

  // Validate progress range
  if (typeof event.progress !== 'number' || event.progress < 0 || event.progress > 100) {
    logger.warn('Invalid progress in ingestion event', { progress: event.progress });
    return false;
  }

  return true;
}

export default {
  initializeIngestionHandlers,
  handleJobUpdate,
  broadcastIngestionEvent,
  validateIngestionEvent,
};
