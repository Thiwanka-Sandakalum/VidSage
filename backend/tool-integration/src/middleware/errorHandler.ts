import { Request, Response, NextFunction } from 'express';
import { ErrorResponse } from '../types';

/**
 * Global error handler middleware
 * Catches all errors and returns a consistent JSON response
 */
export const errorHandler = (
    err: Error,
    _req: Request,
    res: Response,
    _next: NextFunction
): void => {
    console.error('Error occurred:', err);

    // Default error response
    const errorResponse: ErrorResponse = {
        error: 'Internal Server Error',
        message: err.message || 'An unexpected error occurred',
        statusCode: 500,
    };

    // Handle specific error types
    if (err.name === 'ValidationError') {
        errorResponse.statusCode = 400;
        errorResponse.error = 'Validation Error';
    } else if (err.name === 'UnauthorizedError') {
        errorResponse.statusCode = 401;
        errorResponse.error = 'Unauthorized';
    } else if (err.message.includes('not found')) {
        errorResponse.statusCode = 404;
        errorResponse.error = 'Not Found';
    }

    // Include stack trace in development
    if (process.env.NODE_ENV === 'development') {
        errorResponse.details = {
            stack: err.stack,
            name: err.name,
        };
    }

    res.status(errorResponse.statusCode).json(errorResponse);
};

/**
 * Async handler wrapper to catch errors in async route handlers
 * Usage: router.get('/path', asyncHandler(async (req, res) => { ... }))
 */
export const asyncHandler = (
    fn: (req: Request, res: Response, next: NextFunction) => Promise<unknown>
) => {
    return (req: Request, res: Response, next: NextFunction) => {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
};
