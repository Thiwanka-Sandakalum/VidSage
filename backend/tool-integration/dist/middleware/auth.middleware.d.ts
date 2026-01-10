import { Request, Response, NextFunction } from 'express';
/**
 * Middleware to validate Clerk user authentication
 * In production, verify the Clerk session token
 */
export declare const validateClerkAuth: (req: Request, res: Response, next: NextFunction) => void;
export declare const rateLimit: (maxRequests?: number, windowMs?: number) => (req: Request, res: Response, next: NextFunction) => void;
/**
 * Request validation middleware
 */
export declare const validateRequest: (requiredFields: string[]) => (req: Request, res: Response, next: NextFunction) => void;
//# sourceMappingURL=auth.middleware.d.ts.map