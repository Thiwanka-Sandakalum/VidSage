import { UserTokens } from '../types';
/**
 * MongoDB Token Store
 * Securely stores encrypted Google OAuth tokens linked to Clerk user IDs
 */
declare class MongoTokenStore {
    /**
     * Save user tokens to MongoDB
     * @param userId - Clerk user ID
     * @param tokens - Token data to store
     */
    saveTokens(userId: string, tokens: Omit<UserTokens, 'userId' | 'createdAt' | 'updatedAt'>): Promise<void>;
    /**
     * Retrieve user tokens from MongoDB
     * @param userId - Clerk user ID
     * @returns User tokens or null if not found
     */
    getTokens(userId: string): Promise<UserTokens | null>;
    /**
     * Update access token (after refresh)
     * @param userId - Clerk user ID
     * @param accessToken - New access token
     * @param expiryDate - New expiry date
     */
    updateAccessToken(userId: string, accessToken: string, expiryDate: number): Promise<void>;
    /**
     * Delete user tokens from MongoDB
     * @param userId - Clerk user ID
     * @returns True if tokens were deleted, false if not found
     */
    deleteTokens(userId: string): Promise<boolean>;
    /**
     * Check if user has tokens stored
     * @param userId - Clerk user ID
     * @returns True if tokens exist
     */
    hasTokens(userId: string): Promise<boolean>;
    /**
     * Clean up expired tokens (optional maintenance task)
     * Run this periodically via cron job
     */
    cleanupExpiredTokens(): Promise<void>;
}
export declare const tokenStore: MongoTokenStore;
export {};
//# sourceMappingURL=token.service.d.ts.map