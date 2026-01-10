import { google } from 'googleapis';
import dotenv from 'dotenv';

dotenv.config();

/**
 * Validate required environment variables
 */
const validateEnvVars = (): void => {
    const required = ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REDIRECT_URI'];
    const missing = required.filter((key) => !process.env[key]);

    if (missing.length > 0) {
        throw new Error(`Missing required environment variables: ${missing.join(', ')}`);
    }
};

validateEnvVars();

/**
 * Google OAuth 2.0 Client
 * Configured for user data access with offline access and consent prompt
 */
export const oauth2Client = new google.auth.OAuth2(
    process.env.GOOGLE_CLIENT_ID,
    process.env.GOOGLE_CLIENT_SECRET,
    process.env.GOOGLE_REDIRECT_URI
);

/**
 * OAuth scopes required for Google Drive and Docs access
 * - drive.file: Access only files created by this app
 * - documents: Read and write Google Docs
 */
export const GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/documents',
];

/**
 * OAuth configuration
 */
export const OAUTH_CONFIG = {
    access_type: 'offline' as const, // Request refresh token
    prompt: 'consent' as const, // Always show consent screen to ensure refresh token
    scope: GOOGLE_SCOPES,
};
