import request from 'supertest';
import express from 'express';
import googleRoutes from '../../src/routes/google.routes';

// Create Express app for testing
const app = express();
app.use(express.json());
app.use('/', googleRoutes);

// Health check endpoint
app.get('/health', (_req, res) => {
    res.json({
        status: 'healthy',
        service: 'VidSage User Management Service',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
    });
});

describe('Health Check Tests', () => {
    it('should return health status', async () => {
        const response = await request(app).get('/health');

        expect(response.status).toBe(200);
        expect(response.body).toHaveProperty('status', 'healthy');
        expect(response.body).toHaveProperty('service', 'VidSage User Management Service');
        expect(response.body).toHaveProperty('timestamp');
        expect(response.body).toHaveProperty('uptime');
        expect(typeof response.body.uptime).toBe('number');
    });

    it('should return valid ISO timestamp', async () => {
        const response = await request(app).get('/health');

        const timestamp = new Date(response.body.timestamp);
        expect(timestamp.toString()).not.toBe('Invalid Date');
    });
});
