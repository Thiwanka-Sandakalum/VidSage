"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.asyncHandler = exports.errorHandler = void 0;
/**
 * Global error handler middleware
 * Catches all errors and returns a consistent JSON response
 */
const errorHandler = (err, _req, res, _next) => {
    console.error('Error occurred:', err);
    // Default error response
    const errorResponse = {
        error: 'Internal Server Error',
        message: err.message || 'An unexpected error occurred',
        statusCode: 500,
    };
    // Handle specific error types
    if (err.name === 'ValidationError') {
        errorResponse.statusCode = 400;
        errorResponse.error = 'Validation Error';
    }
    else if (err.name === 'UnauthorizedError') {
        errorResponse.statusCode = 401;
        errorResponse.error = 'Unauthorized';
    }
    else if (err.message.includes('not found')) {
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
exports.errorHandler = errorHandler;
/**
 * Async handler wrapper to catch errors in async route handlers
 * Usage: router.get('/path', asyncHandler(async (req, res) => { ... }))
 */
const asyncHandler = (fn) => {
    return (req, res, next) => {
        Promise.resolve(fn(req, res, next)).catch(next);
    };
};
exports.asyncHandler = asyncHandler;
//# sourceMappingURL=errorHandler.js.map