"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.isDatabaseConnected = exports.disconnectDatabase = exports.connectDatabase = void 0;
const mongoose_1 = __importDefault(require("mongoose"));
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/vidsage';
/**
 * Connect to MongoDB database
 */
const connectDatabase = async () => {
    try {
        await mongoose_1.default.connect(MONGODB_URI);
        console.log('✅ MongoDB connected successfully');
        if (mongoose_1.default.connection.db) {
            console.log(`📊 Database: ${mongoose_1.default.connection.db.databaseName}`);
        }
        else {
            console.warn('⚠️  Database connection established, but database information is unavailable.');
        }
        // Handle connection events
        mongoose_1.default.connection.on('error', (error) => {
            console.error('❌ MongoDB connection error:', error);
        });
        mongoose_1.default.connection.on('disconnected', () => {
            console.warn('⚠️  MongoDB disconnected');
        });
        mongoose_1.default.connection.on('reconnected', () => {
            console.log('✅ MongoDB reconnected');
        });
    }
    catch (error) {
        console.error('❌ Failed to connect to MongoDB:', error);
        // In production, you might want to exit the process or implement retry logic
        throw error;
    }
};
exports.connectDatabase = connectDatabase;
/**
 * Disconnect from MongoDB
 */
const disconnectDatabase = async () => {
    try {
        await mongoose_1.default.connection.close();
        console.log('✅ MongoDB connection closed');
    }
    catch (error) {
        console.error('❌ Error closing MongoDB connection:', error);
        throw error;
    }
};
exports.disconnectDatabase = disconnectDatabase;
/**
 * Check if database is connected
 */
const isDatabaseConnected = () => {
    return mongoose_1.default.connection.readyState === 1;
};
exports.isDatabaseConnected = isDatabaseConnected;
//# sourceMappingURL=database.js.map