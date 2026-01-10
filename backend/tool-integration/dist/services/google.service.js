"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.listUserDocs = exports.createDriveFolder = exports.createGoogleDoc = exports.isTokenExpired = exports.refreshAccessToken = exports.exchangeCodeForTokens = exports.getGoogleAuthUrl = void 0;
const googleapis_1 = require("googleapis");
const googleOAuth_1 = require("../config/googleOAuth");
/**
 * Generate Google OAuth authorization URL
 * @param state - Optional state parameter for CSRF protection
 * @returns Authorization URL to redirect user to
 */
const getGoogleAuthUrl = (state) => {
    const authUrl = googleOAuth_1.oauth2Client.generateAuthUrl({
        ...googleOAuth_1.OAUTH_CONFIG,
        state: state || undefined,
    });
    return authUrl;
};
exports.getGoogleAuthUrl = getGoogleAuthUrl;
/**
 * Exchange authorization code for access and refresh tokens
 * @param code - Authorization code from Google OAuth callback
 * @returns Token set including access_token and refresh_token
 */
const exchangeCodeForTokens = async (code) => {
    try {
        const { tokens } = await googleOAuth_1.oauth2Client.getToken(code);
        if (!tokens.access_token) {
            throw new Error('No access token received from Google');
        }
        // Ensure token_type is string or undefined (not null)
        return {
            ...tokens,
            token_type: tokens.token_type === null ? undefined : tokens.token_type,
        };
    }
    catch (error) {
        console.error('Error exchanging code for tokens:', error);
        throw new Error('Failed to exchange authorization code for tokens');
    }
};
exports.exchangeCodeForTokens = exchangeCodeForTokens;
/**
 * Refresh an expired access token using the refresh token
 * @param refreshToken - User's refresh token
 * @returns New access token and expiry date
 */
const refreshAccessToken = async (refreshToken) => {
    try {
        googleOAuth_1.oauth2Client.setCredentials({
            refresh_token: refreshToken,
        });
        const { credentials } = await googleOAuth_1.oauth2Client.refreshAccessToken();
        if (!credentials.access_token || !credentials.expiry_date) {
            throw new Error('Failed to refresh access token');
        }
        return {
            accessToken: credentials.access_token,
            expiryDate: credentials.expiry_date,
        };
    }
    catch (error) {
        console.error('Error refreshing access token:', error);
        throw new Error('Failed to refresh access token. User may need to re-authenticate.');
    }
};
exports.refreshAccessToken = refreshAccessToken;
/**
 * Check if access token is expired or about to expire
 * @param expiryDate - Token expiry timestamp
 * @returns True if token is expired or expires within 5 minutes
 */
const isTokenExpired = (expiryDate) => {
    if (!expiryDate)
        return true;
    const now = Date.now();
    const bufferTime = 5 * 60 * 1000; // 5 minutes buffer
    return expiryDate - now < bufferTime;
};
exports.isTokenExpired = isTokenExpired;
/**
 * Set credentials on OAuth client with automatic refresh
 * @param accessToken - Current access token
 * @param refreshToken - Refresh token for renewing access
 * @param expiryDate - Token expiry timestamp
 */
const setClientCredentials = (accessToken, refreshToken, expiryDate) => {
    googleOAuth_1.oauth2Client.setCredentials({
        access_token: accessToken,
        refresh_token: refreshToken || undefined,
        expiry_date: expiryDate || undefined,
    });
};
/**
 * Create a new Google Doc and write content to it
 * @param request - Document creation request with tokens and content
 * @returns Document ID and URL
 */
const createGoogleDoc = async (request) => {
    const { accessToken, refreshToken, expiryDate, content, title, folderId } = request;
    try {
        // Set credentials
        setClientCredentials(accessToken, refreshToken, expiryDate);
        // Initialize Google APIs
        const drive = googleapis_1.google.drive({ version: 'v3', auth: googleOAuth_1.oauth2Client });
        const docs = googleapis_1.google.docs({ version: 'v1', auth: googleOAuth_1.oauth2Client });
        // Create the document
        const fileMetadata = {
            name: title || 'AI Generated Summary',
            mimeType: 'application/vnd.google-apps.document',
        };
        // Optionally add to specific folder
        if (folderId) {
            fileMetadata.parents = [folderId];
        }
        const file = await drive.files.create({
            requestBody: fileMetadata,
            fields: 'id, name, webViewLink',
        });
        if (!file.data.id) {
            throw new Error('Failed to create Google Doc - no document ID returned');
        }
        const documentId = file.data.id;
        // Write content to the document
        await docs.documents.batchUpdate({
            documentId,
            requestBody: {
                requests: [
                    {
                        insertText: {
                            location: { index: 1 },
                            text: content,
                        },
                    },
                ],
            },
        });
        return {
            documentId,
            documentUrl: file.data.webViewLink || `https://docs.google.com/document/d/${documentId}/edit`,
            title: file.data.name || title || 'AI Generated Summary',
        };
    }
    catch (error) {
        console.error('Error creating Google Doc:', error);
        throw new Error('Failed to create Google Doc. Please check your permissions and try again.');
    }
};
exports.createGoogleDoc = createGoogleDoc;
/**
 * Create a folder in Google Drive (optional utility)
 * @param folderName - Name of the folder to create
 * @param accessToken - User's access token
 * @param refreshToken - User's refresh token
 * @returns Folder ID
 */
const createDriveFolder = async (folderName, accessToken, refreshToken) => {
    try {
        setClientCredentials(accessToken, refreshToken);
        const drive = googleapis_1.google.drive({ version: 'v3', auth: googleOAuth_1.oauth2Client });
        const fileMetadata = {
            name: folderName,
            mimeType: 'application/vnd.google-apps.folder',
        };
        const folder = await drive.files.create({
            requestBody: fileMetadata,
            fields: 'id',
        });
        if (!folder.data.id) {
            throw new Error('Failed to create folder');
        }
        return folder.data.id;
    }
    catch (error) {
        console.error('Error creating Drive folder:', error);
        throw new Error('Failed to create Google Drive folder');
    }
};
exports.createDriveFolder = createDriveFolder;
/**
 * List user's Google Docs (optional utility)
 * @param accessToken - User's access token
 * @param refreshToken - User's refresh token
 * @param pageSize - Number of files to return (default 10)
 * @returns List of document metadata
 */
const listUserDocs = async (accessToken, refreshToken, pageSize = 10) => {
    try {
        setClientCredentials(accessToken, refreshToken);
        const drive = googleapis_1.google.drive({ version: 'v3', auth: googleOAuth_1.oauth2Client });
        const response = await drive.files.list({
            pageSize,
            fields: 'files(id, name, webViewLink, createdTime, modifiedTime)',
            q: "mimeType='application/vnd.google-apps.document'",
            orderBy: 'modifiedTime desc',
        });
        return response.data.files || [];
    }
    catch (error) {
        console.error('Error listing user docs:', error);
        throw new Error('Failed to list Google Docs');
    }
};
exports.listUserDocs = listUserDocs;
//# sourceMappingURL=google.service.js.map