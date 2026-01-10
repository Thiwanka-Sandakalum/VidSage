import request from 'supertest';
import express from 'express';
import googleRoutes from '../../src/routes/google.routes';
import { tokenStore } from '../../src/services/token.service';
import * as googleService from '../../src/services/google.service';

// Mock Google services
jest.mock('../../src/services/google.service');

const mockGoogleService = googleService as jest.Mocked<typeof googleService>;

// Create Express app for testing
const app = express();
app.use(express.json());
app.use('/', googleRoutes);

describe('Google Docs Integration Tests', () => {
    const testUserId = 'test_docs_user';

    beforeEach(async () => {
        // Setup mock implementations
        mockGoogleService.isTokenExpired.mockReturnValue(false);
        mockGoogleService.createGoogleDoc.mockResolvedValue({
            documentId: 'test-doc-id-123',
            documentUrl: 'https://docs.google.com/document/d/test-doc-id-123/edit',
            title: 'Test Document',
        });
        mockGoogleService.listUserDocs.mockResolvedValue([
            {
                id: 'doc1',
                name: 'Document 1',
                webViewLink: 'https://docs.google.com/document/d/doc1/edit',
                createdTime: '2026-01-01T10:00:00.000Z',
                modifiedTime: '2026-01-01T11:00:00.000Z',
            },
            {
                id: 'doc2',
                name: 'Document 2',
                webViewLink: 'https://docs.google.com/document/d/doc2/edit',
                createdTime: '2026-01-02T10:00:00.000Z',
                modifiedTime: '2026-01-02T11:00:00.000Z',
            },
        ]);

        // Store test tokens
        await tokenStore.saveTokens(testUserId, {
            accessToken: 'test-access-token',
            refreshToken: 'test-refresh-token',
            expiryDate: Date.now() + 3600000,
            scope: 'https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/documents',
            tokenType: 'Bearer',
        });
    });

    describe('POST /google/docs', () => {
        it('should create a Google Doc with content', async () => {
            const response = await request(app)
                .post('/google/docs')
                .send({
                    userId: testUserId,
                    content: 'This is a test AI-generated summary.',
                    title: 'Test Summary',
                });

            expect(response.status).toBe(201);
            expect(response.body).toHaveProperty('success', true);
            expect(response.body).toHaveProperty('document');
            expect(response.body.document).toMatchObject({
                documentId: 'test-doc-id-123',
                documentUrl: expect.stringContaining('docs.google.com'),
                title: 'Test Document',
            });

            // Verify createGoogleDoc was called with correct parameters
            expect(mockGoogleService.createGoogleDoc).toHaveBeenCalledWith(
                expect.objectContaining({
                    userId: testUserId,
                    content: 'This is a test AI-generated summary.',
                    title: 'Test Summary',
                    accessToken: 'test-access-token',
                    refreshToken: 'test-refresh-token',
                })
            );
        });

        it('should create a Google Doc without optional title', async () => {
            const response = await request(app)
                .post('/google/docs')
                .send({
                    userId: testUserId,
                    content: 'Content without title',
                });

            expect(response.status).toBe(201);
            expect(response.body.success).toBe(true);
            expect(mockGoogleService.createGoogleDoc).toHaveBeenCalled();
        });

        it('should create a Google Doc in specific folder', async () => {
            const response = await request(app)
                .post('/google/docs')
                .send({
                    userId: testUserId,
                    content: 'Content in folder',
                    title: 'Folder Document',
                    folderId: 'test-folder-id-456',
                });

            expect(response.status).toBe(201);
            expect(mockGoogleService.createGoogleDoc).toHaveBeenCalledWith(
                expect.objectContaining({
                    folderId: 'test-folder-id-456',
                })
            );
        });

        it('should return 400 if userId is missing', async () => {
            const response = await request(app)
                .post('/google/docs')
                .send({
                    content: 'Test content',
                });

            expect(response.status).toBe(400);
            expect(response.body).toHaveProperty('error', 'Bad Request');
            expect(response.body.message).toContain('userId and content are required');
        });

        it('should return 400 if content is missing', async () => {
            const response = await request(app)
                .post('/google/docs')
                .send({
                    userId: testUserId,
                });

            expect(response.status).toBe(400);
            expect(response.body).toHaveProperty('error', 'Bad Request');
            expect(response.body.message).toContain('userId and content are required');
        });

        it('should return 401 if user has not authorized Google', async () => {
            const response = await request(app)
                .post('/google/docs')
                .send({
                    userId: 'unauthorized_user',
                    content: 'Test content',
                });

            expect(response.status).toBe(401);
            expect(response.body).toHaveProperty('error', 'Unauthorized');
            expect(response.body).toHaveProperty('requiresAuth', true);
            expect(response.body.message).toContain('not authorized Google access');
        });

        it('should auto-refresh expired token before creating doc', async () => {
            // Mock token as expired
            mockGoogleService.isTokenExpired.mockReturnValue(true);
            mockGoogleService.refreshAccessToken.mockResolvedValue({
                accessToken: 'new-access-token',
                expiryDate: Date.now() + 3600000,
            });

            const response = await request(app)
                .post('/google/docs')
                .send({
                    userId: testUserId,
                    content: 'Content after refresh',
                    title: 'Refreshed Doc',
                });

            expect(response.status).toBe(201);
            expect(mockGoogleService.refreshAccessToken).toHaveBeenCalledWith('test-refresh-token');
            expect(mockGoogleService.createGoogleDoc).toHaveBeenCalledWith(
                expect.objectContaining({
                    accessToken: 'new-access-token',
                })
            );

            // Verify token was updated in store
            const updatedTokens = await tokenStore.getTokens(testUserId);
            expect(updatedTokens?.accessToken).toBe('new-access-token');
        });

        it('should return 401 if token expired and no refresh token', async () => {
            // Create user without refresh token
            const userNoRefresh = 'user_no_refresh';
            await tokenStore.saveTokens(userNoRefresh, {
                accessToken: 'test-access-token',
                refreshToken: null,
                expiryDate: Date.now() - 1000, // Expired
                scope: 'drive.file',
                tokenType: 'Bearer',
            });

            mockGoogleService.isTokenExpired.mockReturnValue(true);

            const response = await request(app)
                .post('/google/docs')
                .send({
                    userId: userNoRefresh,
                    content: 'Test content',
                });

            expect(response.status).toBe(401);
            expect(response.body).toHaveProperty('requiresAuth', true);
            expect(response.body.message).toContain('expired and no refresh token');
        });
    });

    describe('GET /google/docs/list', () => {
        it('should list user\'s Google Docs', async () => {
            const response = await request(app)
                .get('/google/docs/list')
                .query({ userId: testUserId });

            expect(response.status).toBe(200);
            expect(response.body).toHaveProperty('success', true);
            expect(response.body).toHaveProperty('documents');
            expect(response.body.documents).toHaveLength(2);
            expect(response.body.documents[0]).toMatchObject({
                id: 'doc1',
                name: 'Document 1',
                webViewLink: expect.stringContaining('docs.google.com'),
            });

            expect(mockGoogleService.listUserDocs).toHaveBeenCalledWith(
                'test-access-token',
                'test-refresh-token',
                10
            );
        });

        it('should support custom page size', async () => {
            const response = await request(app)
                .get('/google/docs/list')
                .query({ userId: testUserId, pageSize: 25 });

            expect(response.status).toBe(200);
            expect(mockGoogleService.listUserDocs).toHaveBeenCalledWith(
                'test-access-token',
                'test-refresh-token',
                25
            );
        });

        it('should return 400 if userId is missing', async () => {
            const response = await request(app).get('/google/docs/list');

            expect(response.status).toBe(400);
            expect(response.body).toHaveProperty('error', 'Bad Request');
            expect(response.body.message).toContain('userId is required');
        });

        it('should return 401 if user not authorized', async () => {
            const response = await request(app)
                .get('/google/docs/list')
                .query({ userId: 'unauthorized_user' });

            expect(response.status).toBe(401);
            expect(response.body).toHaveProperty('requiresAuth', true);
        });

        it('should auto-refresh token if expired', async () => {
            mockGoogleService.isTokenExpired.mockReturnValue(true);
            mockGoogleService.refreshAccessToken.mockResolvedValue({
                accessToken: 'refreshed-access-token',
                expiryDate: Date.now() + 3600000,
            });

            const response = await request(app)
                .get('/google/docs/list')
                .query({ userId: testUserId });

            expect(response.status).toBe(200);
            expect(mockGoogleService.refreshAccessToken).toHaveBeenCalled();
            expect(mockGoogleService.listUserDocs).toHaveBeenCalledWith(
                'refreshed-access-token',
                expect.any(String),
                10
            );
        });
    });
});
