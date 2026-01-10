/**
 * Test utilities and helper functions
 */

import { UserTokens } from '../../src/types';

/**
 * Create mock user tokens for testing
 */
export const createMockTokens = (userId: string, overrides?: Partial<UserTokens>): Omit<UserTokens, 'createdAt' | 'updatedAt'> => {
    return {
        userId,
        accessToken: 'mock-access-token',
        refreshToken: 'mock-refresh-token',
        expiryDate: Date.now() + 3600000, // 1 hour from now
        scope: 'https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/documents',
        tokenType: 'Bearer',
        ...overrides,
    };
};

/**
 * Create expired token set
 */
export const createExpiredTokens = (userId: string): Omit<UserTokens, 'createdAt' | 'updatedAt'> => {
    return createMockTokens(userId, {
        expiryDate: Date.now() - 1000, // Expired 1 second ago
    });
};

/**
 * Create OAuth state parameter
 */
export const createOAuthState = (userId: string): string => {
    const state = {
        userId,
        timestamp: Date.now(),
        nonce: Math.random().toString(36).substring(7),
    };
    return Buffer.from(JSON.stringify(state)).toString('base64');
};

/**
 * Parse OAuth state parameter
 */
export const parseOAuthState = (stateParam: string): { userId: string; timestamp: number; nonce: string } => {
    const decoded = Buffer.from(stateParam, 'base64').toString('utf-8');
    return JSON.parse(decoded);
};

/**
 * Create mock Google Doc response
 */
export const createMockGoogleDoc = (id: string = 'test-doc-id') => ({
    documentId: id,
    documentUrl: `https://docs.google.com/document/d/${id}/edit`,
    title: 'Test Document',
});

/**
 * Create mock Google Doc metadata
 */
export const createMockDocMetadata = (id: string = 'doc1', name: string = 'Document 1') => ({
    id,
    name,
    webViewLink: `https://docs.google.com/document/d/${id}/edit`,
    createdTime: new Date().toISOString(),
    modifiedTime: new Date().toISOString(),
});

/**
 * Wait for async operations (useful for testing async flows)
 */
export const wait = (ms: number): Promise<void> => {
    return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Generate random user ID for testing
 */
export const generateTestUserId = (): string => {
    return `test_user_${Math.random().toString(36).substring(7)}`;
};

/**
 * Create test content for Google Docs
 */
export const createTestContent = (title: string = 'Test Summary'): string => {
    return `# ${title}

This is a test AI-generated summary.

## Key Points
- Point 1
- Point 2
- Point 3

## Conclusion
This is the conclusion of the test document.`;
};

/**
 * Mock Google OAuth token response
 */
export const mockGoogleTokenResponse = {
    access_token: 'ya29.test-access-token',
    refresh_token: '1//test-refresh-token',
    expiry_date: Date.now() + 3600000,
    scope: 'https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/documents',
    token_type: 'Bearer',
    id_token: 'eyJhbGciOiJSUzI1NiIsImtpZCI6InRlc3QifQ.test.token',
};

/**
 * Create error response object
 */
export const createErrorResponse = (error: string, message: string, statusCode: number = 400) => ({
    error,
    message,
    statusCode,
});
