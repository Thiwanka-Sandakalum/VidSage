import { Router, Request, Response, NextFunction } from 'express';
import {
    getGoogleAuthUrl,
    exchangeCodeForTokens,
    createGoogleDoc,
    isTokenExpired,
    refreshAccessToken,
    listUserDocs,
} from '../services/google.service';
import { tokenStore } from '../services/token.service';
import { CreateDocRequest, OAuthState } from '../types';

const router = Router();

/**
 * Helper function to create OAuth state parameter
 * In production, consider signing this to prevent tampering
 */
const createOAuthState = (userId: string): string => {
    const state: OAuthState = {
        userId,
        timestamp: Date.now(),
        nonce: Math.random().toString(36).substring(7),
    };
    return Buffer.from(JSON.stringify(state)).toString('base64');
};

/**
 * Helper function to parse OAuth state parameter
 */
const parseOAuthState = (stateParam: string): OAuthState => {
    try {
        const decoded = Buffer.from(stateParam, 'base64').toString('utf-8');
        return JSON.parse(decoded);
    } catch (error) {
        throw new Error('Invalid state parameter');
    }
};

/**
 * STEP 1: Initiate Google OAuth flow
 * 
 * GET /auth/google
 * 
 * Query Parameters:
 * - userId: Clerk user ID (required)
 * 
 * This endpoint generates the Google OAuth consent URL and redirects the user.
 * The state parameter contains the userId for security and session tracking.
 */
router.get('/auth/google', (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.userId as string;

        if (!userId) {
            return res.status(400).json({
                error: 'Bad Request',
                message: 'userId is required',
            });
        }

        // Create secure state parameter
        const state = createOAuthState(userId);

        // Generate OAuth URL
        const authUrl = getGoogleAuthUrl(state);

        // Redirect user to Google consent screen
        return res.json({ authUrl });
    } catch (error) {
        return next(error);
    }
});

/**
 * STEP 2: Handle Google OAuth callback
 * 
 * GET /auth/google/callback
 * 
 * Query Parameters:
 * - code: Authorization code from Google
 * - state: State parameter containing userId
 * - error: Error message if user denied consent
 * 
 * This endpoint:
 * 1. Exchanges the authorization code for tokens
 * 2. Stores tokens securely linked to the userId
 * 3. Redirects user back to the frontend application
 */
router.get('/auth/google/callback', async (req: Request, res: Response) => {
    try {
        const { code, state, error } = req.query;

        // Handle user denial
        if (error) {
            return res.redirect(`${process.env.FRONTEND_URL || 'http://localhost:5173'}/oauth/error?error=${error}`);
        }

        // Validate parameters
        if (!code || !state) {
            return res.status(400).json({
                error: 'Bad Request',
                message: 'Missing required parameters',
            });
        }

        // Parse and validate state
        const oauthState = parseOAuthState(state as string);
        const { userId } = oauthState;

        // Exchange code for tokens
        const tokens = await exchangeCodeForTokens(code as string);

        // Store tokens securely
        await tokenStore.saveTokens(userId, {
            accessToken: tokens.access_token!,
            refreshToken: tokens.refresh_token || null,
            expiryDate: tokens.expiry_date || null,
            scope: tokens.scope,
            tokenType: tokens.token_type,
        });

        // Redirect to frontend success page
        const redirectUrl = `${process.env.FRONTEND_URL || 'http://localhost:5173'}/oauth/success`;
        res.redirect(redirectUrl);
    } catch (error) {
        console.error('OAuth callback error:', error);
        const errorUrl = `${process.env.FRONTEND_URL || 'http://localhost:5173'}/oauth/error?error=callback_failed`;
        res.redirect(errorUrl);
    }
});

/**
 * STEP 3: Create Google Doc with AI-generated content
 * 
 * POST /google/docs
 * 
 * Request Body:
 * - userId: Clerk user ID (required)
 * - content: Text content to write to the document (required)
 * - title: Document title (optional, defaults to "AI Generated Summary")
 * - folderId: Google Drive folder ID (optional)
 * 
 * This endpoint:
 * 1. Retrieves stored tokens for the user
 * 2. Refreshes access token if expired
 * 3. Creates a new Google Doc
 * 4. Writes the content to the document
 * 5. Returns the document ID and URL
 */
router.post('/google/docs', async (req: Request, res: Response, next: NextFunction) => {
    try {
        const { userId, content, title, folderId } = req.body as CreateDocRequest;

        // Validate request
        if (!userId || !content) {
            return res.status(400).json({
                error: 'Bad Request',
                message: 'userId and content are required',
            });
        }

        // Retrieve stored tokens
        const storedTokens = await tokenStore.getTokens(userId);

        if (!storedTokens) {
            return res.status(401).json({
                error: 'Unauthorized',
                message: 'User has not authorized Google access. Please authenticate first.',
                requiresAuth: true,
            });
        }

        let { accessToken, refreshToken, expiryDate } = storedTokens;

        // Refresh token if expired
        if (isTokenExpired(expiryDate)) {
            if (!refreshToken) {
                return res.status(401).json({
                    error: 'Unauthorized',
                    message: 'Access token expired and no refresh token available. Please re-authenticate.',
                    requiresAuth: true,
                });
            }

            console.log('Access token expired, refreshing...');
            const refreshed = await refreshAccessToken(refreshToken);
            accessToken = refreshed.accessToken;
            expiryDate = refreshed.expiryDate;

            // Update stored tokens
            await tokenStore.updateAccessToken(userId, accessToken, expiryDate);
        }

        // Create Google Doc
        const document = await createGoogleDoc({
            userId,
            content,
            title,
            folderId,
            accessToken,
            refreshToken,
            expiryDate,
        });

        res.status(201).json({
            success: true,
            document,
        });
    } catch (error) {
        return next(error);
    }
});

/**
 * Check user's Google OAuth status
 * 
 * GET /google/status
 * 
 * Query Parameters:
 * - userId: Clerk user ID (required)
 * 
 * Returns whether the user has authorized Google access
 */
router.get('/google/status', async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.userId as string;

        if (!userId) {
            return res.status(400).json({
                error: 'Bad Request',
                message: 'userId is required',
            });
        }

        const hasTokens = await tokenStore.hasTokens(userId);
        const tokens = hasTokens ? await tokenStore.getTokens(userId) : null;

        res.json({
            authorized: hasTokens,
            hasRefreshToken: tokens?.refreshToken ? true : false,
            tokenExpired: tokens ? isTokenExpired(tokens.expiryDate) : null,
        });
    } catch (error) {
        return next(error);
    }
});

/**
 * Revoke Google OAuth access
 * 
 * DELETE /google/revoke
 * 
 * Request Body:
 * - userId: Clerk user ID (required)
 * 
 * Deletes stored tokens and revokes access
 */
router.delete('/google/revoke', async (req: Request, res: Response, next: NextFunction) => {
    try {
        const { userId } = req.body;

        if (!userId) {
            return res.status(400).json({
                error: 'Bad Request',
                message: 'userId is required',
            });
        }

        await tokenStore.deleteTokens(userId);

        res.json({
            success: true,
            message: 'Google access revoked successfully',
        });
    } catch (error) {
        return next(error);
    }
});

/**
 * List user's Google Docs (Optional utility endpoint)
 * 
 * GET /google/docs/list
 * 
 * Query Parameters:
 * - userId: Clerk user ID (required)
 * - pageSize: Number of documents to return (optional, default 10)
 */
router.get('/google/docs/list', async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.userId as string;
        const pageSize = parseInt(req.query.pageSize as string) || 10;

        if (!userId) {
            return res.status(400).json({
                error: 'Bad Request',
                message: 'userId is required',
            });
        }

        const storedTokens = await tokenStore.getTokens(userId);

        if (!storedTokens) {
            return res.status(401).json({
                error: 'Unauthorized',
                message: 'User has not authorized Google access',
                requiresAuth: true,
            });
        }

        let { accessToken, refreshToken, expiryDate } = storedTokens;

        // Refresh token if expired
        if (isTokenExpired(expiryDate)) {
            if (!refreshToken) {
                return res.status(401).json({
                    error: 'Unauthorized',
                    message: 'Access token expired. Please re-authenticate.',
                    requiresAuth: true,
                });
            }

            const refreshed = await refreshAccessToken(refreshToken);
            accessToken = refreshed.accessToken;
            expiryDate = refreshed.expiryDate;

            await tokenStore.updateAccessToken(userId, accessToken, expiryDate);
        }

        const docs = await listUserDocs(accessToken, refreshToken, pageSize);

        res.json({
            success: true,
            documents: docs,
        });
    } catch (error) {
        return next(error);
    }
});

// Duplicate '/google/status' route removed to avoid conflicts and unreachable code paths.

/**
 * Disconnect Google account
 * 
 * DELETE /google/disconnect
 * 
 * Query Parameters:
 * - userId: Clerk user ID (required)
 */
router.delete('/google/disconnect', async (req: Request, res: Response, next: NextFunction) => {
    try {
        const userId = req.query.userId as string;

        if (!userId) {
            return res.status(400).json({
                error: 'Bad Request',
                message: 'userId is required',
            });
        }

        const deleted = await tokenStore.deleteTokens(userId);

        if (!deleted) {
            return res.status(404).json({
                error: 'Not Found',
                message: 'Google account not connected',
            });
        }

        res.json({
            success: true,
            message: 'Google account disconnected successfully'
        });
    } catch (error) {
        return next(error);
    }
});

export default router;
