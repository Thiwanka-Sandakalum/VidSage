import { GoogleTokens, CreateDocRequest, CreateDocResponse, RefreshTokenResponse } from '../types';
/**
 * Generate Google OAuth authorization URL
 * @param state - Optional state parameter for CSRF protection
 * @returns Authorization URL to redirect user to
 */
export declare const getGoogleAuthUrl: (state?: string) => string;
/**
 * Exchange authorization code for access and refresh tokens
 * @param code - Authorization code from Google OAuth callback
 * @returns Token set including access_token and refresh_token
 */
export declare const exchangeCodeForTokens: (code: string) => Promise<GoogleTokens>;
/**
 * Refresh an expired access token using the refresh token
 * @param refreshToken - User's refresh token
 * @returns New access token and expiry date
 */
export declare const refreshAccessToken: (refreshToken: string) => Promise<RefreshTokenResponse>;
/**
 * Check if access token is expired or about to expire
 * @param expiryDate - Token expiry timestamp
 * @returns True if token is expired or expires within 5 minutes
 */
export declare const isTokenExpired: (expiryDate: number | null | undefined) => boolean;
/**
 * Create a new Google Doc and write content to it
 * @param request - Document creation request with tokens and content
 * @returns Document ID and URL
 */
export declare const createGoogleDoc: (request: CreateDocRequest & {
    accessToken: string;
    refreshToken: string | null;
    expiryDate?: number | null;
}) => Promise<CreateDocResponse>;
/**
 * Create a folder in Google Drive (optional utility)
 * @param folderName - Name of the folder to create
 * @param accessToken - User's access token
 * @param refreshToken - User's refresh token
 * @returns Folder ID
 */
export declare const createDriveFolder: (folderName: string, accessToken: string, refreshToken: string | null) => Promise<string>;
/**
 * List user's Google Docs (optional utility)
 * @param accessToken - User's access token
 * @param refreshToken - User's refresh token
 * @param pageSize - Number of files to return (default 10)
 * @returns List of document metadata
 */
export declare const listUserDocs: (accessToken: string, refreshToken: string | null, pageSize?: number) => Promise<import("googleapis").drive_v3.Schema$File[]>;
//# sourceMappingURL=google.service.d.ts.map