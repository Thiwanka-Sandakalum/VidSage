"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateRequest = exports.rateLimit = exports.validateClerkAuth = void 0;
/**
 * Middleware to validate Clerk user authentication
 * In production, verify the Clerk session token
 */
const validateClerkAuth = (req, res, next) => {
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
    req.userId = userId;
    next();
};
exports.validateClerkAuth = validateClerkAuth;
/**
 * Rate limiting middleware (simple in-memory implementation)
 * In production, use Redis-based rate limiting
 */
const rateLimitStore = new Map();
const rateLimit = (maxRequests = 10, windowMs = 60000) => {
    return (req, res, next) => {
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
exports.rateLimit = rateLimit;
/**
 * Request validation middleware
 */
const validateRequest = (requiredFields) => {
    return (req, res, next) => {
        const missingFields = [];
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
exports.validateRequest = validateRequest;
//# sourceMappingURL=auth.middleware.js.map