import mongoose from 'mongoose';
import dotenv from 'dotenv';

dotenv.config();

const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/vidsage';

/**
 * Connect to MongoDB database
 */
export const connectDatabase = async (): Promise<void> => {
    try {
        await mongoose.connect(MONGODB_URI);

        console.log('✅ MongoDB connected successfully');
        if (mongoose.connection.db) {
            console.log(`📊 Database: ${mongoose.connection.db.databaseName}`);
        } else {
            console.warn('⚠️  Database connection established, but database information is unavailable.');
        }

        // Handle connection events
        mongoose.connection.on('error', (error) => {
            console.error('❌ MongoDB connection error:', error);
        });

        mongoose.connection.on('disconnected', () => {
            console.warn('⚠️  MongoDB disconnected');
        });

        mongoose.connection.on('reconnected', () => {
            console.log('✅ MongoDB reconnected');
        });
    } catch (error) {
        console.error('❌ Failed to connect to MongoDB:', error);
        // In production, you might want to exit the process or implement retry logic
        throw error;
    }
};

/**
 * Disconnect from MongoDB
 */
export const disconnectDatabase = async (): Promise<void> => {
    try {
        await mongoose.connection.close();
        console.log('✅ MongoDB connection closed');
    } catch (error) {
        console.error('❌ Error closing MongoDB connection:', error);
        throw error;
    }
};

/**
 * Check if database is connected
 */
export const isDatabaseConnected = (): boolean => {
    return mongoose.connection.readyState === 1;
};
