import { Request, Response, NextFunction } from 'express';

/**
 * Middleware to validate Clerk user authentication
 * In production, verify the Clerk session token
 */
export const validateClerkAuth = (req: Request, res: Response, next: NextFunction): void => {
    // Extract userId from request (from query, body, or headers)
    const userId = req.body?.userId || req.query?.userId || req.headers['x-user-id'];

    if (!userId) {
        res.status(401).json({
            error: 'Unauthorized',
            message: 'No user ID provided. Please authenticate with Clerk.',
        });
        return;
    }

    // In production, verify Clerk session token here
    // Example:
    // const sessionToken = req.headers.authorization?.replace('Bearer ', '');
    // const session = await clerkClient.verifyToken(sessionToken);
    // if (!session || session.userId !== userId) {
    //   return res.status(401).json({ error: 'Invalid session' });
    // }

    // Attach userId to request for downstream use
    (req as any).userId = userId;

    next();
};

/**
 * Rate limiting middleware (simple in-memory implementation)
 * In production, use Redis-based rate limiting
 */
const rateLimitStore = new Map<string, { count: number; resetTime: number }>();

export const rateLimit = (maxRequests: number = 10, windowMs: number = 60000) => {
    return (req: Request, res: Response, next: NextFunction): void => {
        const key = req.ip || 'unknown';
        const now = Date.now();

        const record = rateLimitStore.get(key);

        if (!record || now > record.resetTime) {
            // Create new record
            rateLimitStore.set(key, {
                count: 1,
                resetTime: now + windowMs,
            });
            next();
            return;
        }

        if (record.count >= maxRequests) {
            res.status(429).json({
                error: 'Too Many Requests',
                message: 'Rate limit exceeded. Please try again later.',
                retryAfter: Math.ceil((record.resetTime - now) / 1000),
            });
            return;
        }

        // Increment count
        record.count++;
        rateLimitStore.set(key, record);
        next();
    };
};

/**
 * Request validation middleware
 */
export const validateRequest = (requiredFields: string[]) => {
    return (req: Request, res: Response, next: NextFunction): void => {
        const missingFields: string[] = [];

        for (const field of requiredFields) {
            if (!req.body[field]) {
                missingFields.push(field);
            }
        }

        if (missingFields.length > 0) {
            res.status(400).json({
                error: 'Bad Request',
                message: 'Missing required fields',
                missingFields,
            });
            return;
        }

        next();
    };
};
