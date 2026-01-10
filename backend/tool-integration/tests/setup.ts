import { MongoMemoryServer } from 'mongodb-memory-server';
import mongoose from 'mongoose';
import dotenv from 'dotenv';

// Load test environment variables
dotenv.config({ path: '.env.test' });

let mongoServer: MongoMemoryServer;

/**
 * Connect to in-memory MongoDB before all tests
 */
beforeAll(async () => {
    // Create in-memory MongoDB instance
    mongoServer = await MongoMemoryServer.create();
    const mongoUri = mongoServer.getUri();

    // Disconnect if already connected
    if (mongoose.connection.readyState !== 0) {
        await mongoose.disconnect();
    }

    // Connect to in-memory database
    await mongoose.connect(mongoUri);
});

/**
 * Clear all test data after each test
 */
afterEach(async () => {
    const collections = mongoose.connection.collections;
    for (const key in collections) {
        await collections[key].deleteMany({});
    }
});

/**
 * Close database connection and stop MongoDB instance after all tests
 */
afterAll(async () => {
    if (mongoose.connection.readyState !== 0) {
        await mongoose.disconnect();
    }

    if (mongoServer) {
        await mongoServer.stop();
    }
});

/**
 * Set test timeout
 */
jest.setTimeout(30000);

/**
 * Suppress console logs during tests (optional)
 */
global.console = {
    ...console,
    log: jest.fn(),
    debug: jest.fn(),
    info: jest.fn(),
    warn: jest.fn(),
    error: jest.fn(),
};
