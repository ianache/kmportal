import { UserSession } from '../middleware/session';

declare global {
  namespace Express {
    interface Request {
      user?: UserSession;
    }
  }
}

export {};
