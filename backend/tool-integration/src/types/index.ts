import { Credentials } from 'google-auth-library';

/**
 * Stored user token information
 */
export interface UserTokens {
    userId: string; // Clerk user ID
    accessToken: string;
    refreshToken: string | null;
    expiryDate: number | null | undefined;
    scope?: string;
    tokenType?: string;
    createdAt: Date;
    updatedAt: Date;
}

/**
 * Google OAuth token response
 */
export interface GoogleTokens extends Credentials {
    access_token?: string | null;
    refresh_token?: string | null;
    expiry_date?: number | null;
    scope?: string;
    token_type?: string;
    id_token?: string | null;
}

/**
 * Request to create a Google Doc
 */
export interface CreateDocRequest {
    userId: string;
    content: string;
    title?: string;
    folderId?: string; // Optional: create in specific folder
}

/**
 * Google Doc creation response
 */
export interface CreateDocResponse {
    documentId: string;
    documentUrl: string;
    title: string;
}

/**
 * OAuth state parameter for security
 */
export interface OAuthState {
    userId: string;
    timestamp: number;
    nonce: string;
}

/**
 * Token refresh response
 */
export interface RefreshTokenResponse {
    accessToken: string;
    expiryDate: number;
}

/**
 * Error response structure
 */
export interface ErrorResponse {
    error: string;
    message: string;
    statusCode: number;
    details?: unknown;
}
