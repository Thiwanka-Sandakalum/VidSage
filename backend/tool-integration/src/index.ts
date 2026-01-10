import express, { Application, Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import dotenv from 'dotenv';
import googleRoutes from './routes/google.routes';
import { errorHandler } from './middleware/errorHandler';
import { connectDatabase, disconnectDatabase } from './config/database';
import { validateEncryptionKey } from './utils/encryption';

// Load environment variables
dotenv.config();

// Validate encryption key
validateEncryptionKey();

// Create Express application
const app: Application = express();

// Port configuration
const PORT = process.env.PORT || 4000;
const NODE_ENV = process.env.NODE_ENV || 'development';

/**
 * Middleware Configuration
 */

// Security headers
app.use(helmet());

// CORS configuration
app.use(
    cors({
        origin: '*',
        credentials: true,
    })
);

// Body parsers
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging (development only)
if (NODE_ENV === 'development') {
    app.use(morgan('dev'));
} else {
    app.use(morgan('combined'));
}

/**
 * Health Check Endpoint
 */
app.get('/health', (_req: Request, res: Response) => {
    res.json({
        status: 'healthy',
        service: 'VidSage User Management Service',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
    });
});

/**
 * API Routes
 */
app.use('/', googleRoutes);

/**
 * 404 Handler
 */
app.use((_req: Request, res: Response) => {
    res.status(404).json({
        error: 'Not Found',
        message: 'The requested resource was not found',
    });
});

/**
 * Global Error Handler
 */
app.use(errorHandler);

/**
 * Start Server
 */
const startServer = async () => {
    try {
        // Connect to MongoDB first
        await connectDatabase();

        // Start Express server
        const server = app.listen(PORT, () => {
            console.log('='.repeat(50));
            console.log(`🚀 VidSage User Management Service`);
            console.log(`📍 Environment: ${NODE_ENV}`);
            console.log(`🌐 Server running on: http://localhost:${PORT}`);
            console.log(`❤️  Health check: http://localhost:${PORT}/health`);
            console.log('='.repeat(50));
        });

        /**
         * Graceful Shutdown
         */
        const gracefulShutdown = async (signal: string) => {
            console.log(`\n${signal} received. Starting graceful shutdown...`);

            server.close(async () => {
                console.log('✅ HTTP server closed');

                // Disconnect from MongoDB
                await disconnectDatabase();

                process.exit(0);
            });

            // Force shutdown after 10 seconds
            setTimeout(() => {
                console.error('⚠️  Forced shutdown after timeout');
                process.exit(1);
            }, 10000);
        };

        process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
        process.on('SIGINT', () => gracefulShutdown('SIGINT'));
    } catch (error) {
        console.error('❌ Failed to start server:', error);
        process.exit(1);
    }
};

// Start the server
startServer();
