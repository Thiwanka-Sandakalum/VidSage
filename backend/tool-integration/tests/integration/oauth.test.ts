import request from 'supertest';
import express from 'express';
import googleRoutes from '../../src/routes/google.routes';
import { tokenStore } from '../../src/services/token.service';

// Add this import for jest types
import '@jest/globals';

// Mock Google services
jest.mock('../../src/services/google.service', () => ({
    getGoogleAuthUrl: jest.fn((state?: string) => {
        return `https://accounts.google.com/o/oauth2/v2/auth?client_id=test&redirect_uri=http://localhost:5000/auth/google/callback&state=${state || ''}`;
    }),
    exchangeCodeForTokens: jest.fn(async () => ({
        access_token: 'test-access-token',
        refresh_token: 'test-refresh-token',
        expiry_date: Date.now() + 3600000,
        scope: 'https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/documents',
        token_type: 'Bearer',
    })),
    isTokenExpired: jest.fn(() => false),
    refreshAccessToken: jest.fn(async () => ({
        accessToken: 'new-access-token',
        expiryDate: Date.now() + 3600000,
    })),
}));

// Create Express app for testing
const app = express();
app.use(express.json());
app.use('/', googleRoutes);

describe('OAuth Integration Tests', () => {
    describe('GET /auth/google', () => {
        it('should redirect to Google OAuth URL with userId', async () => {
            const userId = 'test_user_123';
            const response = await request(app)
                .get('/auth/google')
                .query({ userId });

            expect([200, 302]).toContain(response.status);
            if (response.status === 302) {
                expect(response.headers.location).toContain('accounts.google.com');
                expect(response.headers.location).toContain('client_id=test');
            }
        });

        it('should return 400 if userId is missing', async () => {
            const response = await request(app).get('/auth/google');

            expect(response.status).toBe(400);
            expect(response.body).toHaveProperty('error', 'Bad Request');
            expect(response.body).toHaveProperty('message', 'userId is required');
        });

        it('should include state parameter in OAuth URL', async () => {
            const userId = 'test_user_456';
            const response = await request(app)
                .get('/auth/google')
                .query({ userId });

            expect([200, 302]).toContain(response.status);
            if (response.status === 302) {
                expect(response.headers.location).toContain('state=');

                // Verify state can be decoded
                const url = new URL(response.headers.location);
                const state = url.searchParams.get('state');
                expect(state).toBeTruthy();

                const decodedState = JSON.parse(Buffer.from(state!, 'base64').toString('utf-8'));
                expect(decodedState).toHaveProperty('userId', userId);
                expect(decodedState).toHaveProperty('timestamp');
                expect(decodedState).toHaveProperty('nonce');
            }
        });
    });

    describe('GET /auth/google/callback', () => {
        it('should exchange code for tokens and store them', async () => {
            const userId = 'test_user_789';
            const state = Buffer.from(
                JSON.stringify({
                    userId,
                    timestamp: Date.now(),
                    nonce: 'test-nonce',
                })
            ).toString('base64');

            const response = await request(app)
                .get('/auth/google/callback')
                .query({
                    code: 'test-auth-code',
                    state,
                });

            expect(response.status).toBe(302);
            expect(response.headers.location).toContain('/oauth/success');

            // Verify tokens were stored
            const storedTokens = await tokenStore.getTokens(userId);
            expect(storedTokens).toBeTruthy();
            expect(storedTokens?.accessToken).toBe('test-access-token');
            expect(storedTokens?.refreshToken).toBe('test-refresh-token');
        });

        it('should redirect to error page if code is missing', async () => {
            const state = Buffer.from(
                JSON.stringify({
                    userId: 'test_user',
                    timestamp: Date.now(),
                    nonce: 'nonce',
                })
            ).toString('base64');

            const response = await request(app)
                .get('/auth/google/callback')
                .query({ state });

            expect([302, 400]).toContain(response.status);
            if (response.status === 302) {
                expect(response.headers.location).toContain('/oauth/error');
            } else {
                expect(response.body).toHaveProperty('error');
            }
        });

        it('should redirect to error page if state is missing', async () => {
            const response = await request(app)
                .get('/auth/google/callback')
                .query({ code: 'test-code' });

            expect([302, 400]).toContain(response.status);
            if (response.status === 302) {
                expect(response.headers.location).toContain('/oauth/error');
            } else {
                expect(response.body).toHaveProperty('error');
            }
        });

        it('should handle user denial (error parameter)', async () => {
            const response = await request(app)
                .get('/auth/google/callback')
                .query({ error: 'access_denied' });

            expect(response.status).toBe(302);
            expect(response.headers.location).toContain('/oauth/error');
            expect(response.headers.location).toContain('error=access_denied');
        });

        it('should redirect to error page on invalid state', async () => {
            const response = await request(app)
                .get('/auth/google/callback')
                .query({
                    code: 'test-code',
                    state: 'invalid-base64',
                });

            expect(response.status).toBe(302);
            expect(response.headers.location).toContain('/oauth/error');
        });
    });

    describe('GET /google/status', () => {
        it('should return authorized=false for non-existent user', async () => {
            const response = await request(app)
                .get('/google/status')
                .query({ userId: 'non_existent_user' });

            expect(response.status).toBe(200);
            expect(response.body).toEqual({
                authorized: false,
                hasRefreshToken: false,
                tokenExpired: null,
            });
        });

        it('should return authorized=true for user with tokens', async () => {
            const userId = 'user_with_tokens';

            // Store tokens first
            await tokenStore.saveTokens(userId, {
                accessToken: 'test-access-token',
                refreshToken: 'test-refresh-token',
                expiryDate: Date.now() + 3600000,
                scope: 'drive.file documents',
                tokenType: 'Bearer',
            });

            const response = await request(app)
                .get('/google/status')
                .query({ userId });

            expect(response.status).toBe(200);
            expect(response.body).toHaveProperty('authorized', true);
            expect(response.body).toHaveProperty('hasRefreshToken', true);
            expect(response.body).toHaveProperty('tokenExpired', false);
        });

        it('should return 400 if userId is missing', async () => {
            const response = await request(app).get('/google/status');

            expect(response.status).toBe(400);
            expect(response.body).toHaveProperty('error', 'Bad Request');
            expect(response.body).toHaveProperty('message', 'userId is required');
        });
    });

    describe('DELETE /google/revoke', () => {
        it('should delete stored tokens', async () => {
            const userId = 'user_to_revoke';

            // Store tokens first
            await tokenStore.saveTokens(userId, {
                accessToken: 'test-access-token',
                refreshToken: 'test-refresh-token',
                expiryDate: Date.now() + 3600000,
                scope: 'drive.file documents',
                tokenType: 'Bearer',
            });

            // Verify tokens exist
            let tokens = await tokenStore.getTokens(userId);
            expect(tokens).toBeTruthy();

            // Revoke access
            const response = await request(app)
                .delete('/google/revoke')
                .send({ userId });

            expect(response.status).toBe(200);
            expect(response.body).toHaveProperty('success', true);
            expect(response.body).toHaveProperty('message', 'Google access revoked successfully');

            // Verify tokens were deleted
            tokens = await tokenStore.getTokens(userId);
            expect(tokens).toBeNull();
        });

        it('should return 400 if userId is missing', async () => {
            const response = await request(app)
                .delete('/google/revoke')
                .send({});

            expect(response.status).toBe(400);
            expect(response.body).toHaveProperty('error', 'Bad Request');
            expect(response.body).toHaveProperty('message', 'userId is required');
        });

        it('should succeed even if user has no tokens', async () => {
            const response = await request(app)
                .delete('/google/revoke')
                .send({ userId: 'non_existent_user' });

            expect(response.status).toBe(200);
            expect(response.body).toHaveProperty('success', true);
        });
    });
});
