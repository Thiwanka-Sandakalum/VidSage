"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.OAUTH_CONFIG = exports.GOOGLE_SCOPES = exports.oauth2Client = void 0;
const googleapis_1 = require("googleapis");
const dotenv_1 = __importDefault(require("dotenv"));
dotenv_1.default.config();
/**
 * Validate required environment variables
 */
const validateEnvVars = () => {
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
exports.oauth2Client = new googleapis_1.google.auth.OAuth2(process.env.GOOGLE_CLIENT_ID, process.env.GOOGLE_CLIENT_SECRET, process.env.GOOGLE_REDIRECT_URI);
/**
 * OAuth scopes required for Google Drive and Docs access
 * - drive.file: Access only files created by this app
 * - documents: Read and write Google Docs
 */
exports.GOOGLE_SCOPES = [
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/documents',
];
/**
 * OAuth configuration
 */
exports.OAUTH_CONFIG = {
    access_type: 'offline', // Request refresh token
    prompt: 'consent', // Always show consent screen to ensure refresh token
    scope: exports.GOOGLE_SCOPES,
};
//# sourceMappingURL=googleOAuth.js.map