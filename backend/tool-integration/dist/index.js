"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = __importDefault(require("express"));
const cors_1 = __importDefault(require("cors"));
const helmet_1 = __importDefault(require("helmet"));
const morgan_1 = __importDefault(require("morgan"));
const dotenv_1 = __importDefault(require("dotenv"));
const google_routes_1 = __importDefault(require("./routes/google.routes"));
const errorHandler_1 = require("./middleware/errorHandler");
const database_1 = require("./config/database");
const encryption_1 = require("./utils/encryption");
// Load environment variables
dotenv_1.default.config();
// Validate encryption key
(0, encryption_1.validateEncryptionKey)();
// Create Express application
const app = (0, express_1.default)();
// Port configuration
const PORT = process.env.PORT || 4000;
const NODE_ENV = process.env.NODE_ENV || 'development';
/**
 * Middleware Configuration
 */
// Security headers
app.use((0, helmet_1.default)());
// CORS configuration
app.use((0, cors_1.default)({
    origin: '*',
    credentials: true,
}));
// Body parsers
app.use(express_1.default.json());
app.use(express_1.default.urlencoded({ extended: true }));
// Request logging (development only)
if (NODE_ENV === 'development') {
    app.use((0, morgan_1.default)('dev'));
}
else {
    app.use((0, morgan_1.default)('combined'));
}
/**
 * Health Check Endpoint
 */
app.get('/health', (_req, res) => {
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
app.use('/', google_routes_1.default);
/**
 * 404 Handler
 */
app.use((_req, res) => {
    res.status(404).json({
        error: 'Not Found',
        message: 'The requested resource was not found',
    });
});
/**
 * Global Error Handler
 */
app.use(errorHandler_1.errorHandler);
/**
 * Start Server
 */
const startServer = async () => {
    try {
        // Connect to MongoDB first
        await (0, database_1.connectDatabase)();
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
        const gracefulShutdown = async (signal) => {
            console.log(`\n${signal} received. Starting graceful shutdown...`);
            server.close(async () => {
                console.log('✅ HTTP server closed');
                // Disconnect from MongoDB
                await (0, database_1.disconnectDatabase)();
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
    }
    catch (error) {
        console.error('❌ Failed to start server:', error);
        process.exit(1);
    }
};
// Start the server
startServer();
//# sourceMappingURL=index.js.map