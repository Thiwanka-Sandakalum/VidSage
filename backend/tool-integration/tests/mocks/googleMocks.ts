/**
 * Mock implementations for Google services
 */

export const mockGoogleService = {
    getGoogleAuthUrl: jest.fn((state?: string) => {
        const baseUrl = 'https://accounts.google.com/o/oauth2/v2/auth';
        const params = new URLSearchParams({
            client_id: process.env.GOOGLE_CLIENT_ID || 'test-client-id',
            redirect_uri: process.env.GOOGLE_REDIRECT_URI || 'http://localhost:5000/auth/google/callback',
            response_type: 'code',
            scope: 'https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/documents',
            access_type: 'offline',
            prompt: 'consent',
            ...(state && { state }),
        });
        return `${baseUrl}?${params.toString()}`;
    }),

    exchangeCodeForTokens: jest.fn(async (code: string) => {
        if (code === 'invalid-code') {
            throw new Error('Invalid authorization code');
        }
        return {
            access_token: 'ya29.mock-access-token',
            refresh_token: '1//mock-refresh-token',
            expiry_date: Date.now() + 3600000,
            scope: 'https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/documents',
            token_type: 'Bearer',
        };
    }),

    refreshAccessToken: jest.fn(async (refreshToken: string) => {
        if (refreshToken === 'invalid-refresh-token') {
            throw new Error('Invalid refresh token');
        }
        return {
            accessToken: 'ya29.new-access-token',
            expiryDate: Date.now() + 3600000,
        };
    }),

    isTokenExpired: jest.fn((expiryDate: number | null | undefined) => {
        if (!expiryDate) return true;
        const now = Date.now();
        const bufferTime = 5 * 60 * 1000; // 5 minutes
        return expiryDate - now < bufferTime;
    }),

    createGoogleDoc: jest.fn(async (request: any) => {
        return {
            documentId: 'mock-doc-id-' + Date.now(),
            documentUrl: `https://docs.google.com/document/d/mock-doc-id-${Date.now()}/edit`,
            title: request.title || 'AI Generated Summary',
        };
    }),

    listUserDocs: jest.fn(async (accessToken: string, refreshToken: string | null, pageSize: number = 10) => {
        const mockDocs = [];
        for (let i = 0; i < Math.min(pageSize, 5); i++) {
            mockDocs.push({
                id: `mock-doc-${i + 1}`,
                name: `Mock Document ${i + 1}`,
                webViewLink: `https://docs.google.com/document/d/mock-doc-${i + 1}/edit`,
                createdTime: new Date(Date.now() - (i + 1) * 86400000).toISOString(),
                modifiedTime: new Date(Date.now() - i * 43200000).toISOString(),
            });
        }
        return mockDocs;
    }),

    createDriveFolder: jest.fn(async (folderName: string) => {
        return `mock-folder-id-${Date.now()}`;
    }),
};

/**
 * Mock googleapis module
 */
export const mockGoogleApis = {
    google: {
        auth: {
            OAuth2: jest.fn().mockImplementation(() => ({
                generateAuthUrl: mockGoogleService.getGoogleAuthUrl,
                getToken: mockGoogleService.exchangeCodeForTokens,
                setCredentials: jest.fn(),
                refreshAccessToken: jest.fn().mockResolvedValue({
                    credentials: {
                        access_token: 'ya29.new-access-token',
                        expiry_date: Date.now() + 3600000,
                    },
                }),
            })),
        },
        drive: jest.fn(() => ({
            files: {
                create: jest.fn().mockResolvedValue({
                    data: {
                        id: 'mock-doc-id',
                        name: 'Mock Document',
                        webViewLink: 'https://docs.google.com/document/d/mock-doc-id/edit',
                    },
                }),
                list: jest.fn().mockResolvedValue({
                    data: {
                        files: [
                            {
                                id: 'doc1',
                                name: 'Document 1',
                                webViewLink: 'https://docs.google.com/document/d/doc1/edit',
                                createdTime: new Date().toISOString(),
                                modifiedTime: new Date().toISOString(),
                            },
                        ],
                    },
                }),
            },
        })),
        docs: jest.fn(() => ({
            documents: {
                batchUpdate: jest.fn().mockResolvedValue({
                    data: {
                        documentId: 'mock-doc-id',
                    },
                }),
            },
        })),
    },
};

/**
 * Reset all mocks
 */
export const resetAllMocks = () => {
    Object.values(mockGoogleService).forEach((mock) => {
        if (jest.isMockFunction(mock)) {
            mock.mockClear();
        }
    });
};
