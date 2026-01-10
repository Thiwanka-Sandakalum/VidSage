/**
 * Google OAuth 2.0 Client
 * Configured for user data access with offline access and consent prompt
 */
export declare const oauth2Client: import("google-auth-library").OAuth2Client;
/**
 * OAuth scopes required for Google Drive and Docs access
 * - drive.file: Access only files created by this app
 * - documents: Read and write Google Docs
 */
export declare const GOOGLE_SCOPES: string[];
/**
 * OAuth configuration
 */
export declare const OAUTH_CONFIG: {
    access_type: "offline";
    prompt: "consent";
    scope: string[];
};
//# sourceMappingURL=googleOAuth.d.ts.map