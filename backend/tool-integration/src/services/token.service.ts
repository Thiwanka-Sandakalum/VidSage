import { UserTokens } from '../types';
import { UserTokensModel } from '../models/UserTokens.model';
import { encrypt, decrypt } from '../utils/encryption';

/**
 * MongoDB Token Store
 * Securely stores encrypted Google OAuth tokens linked to Clerk user IDs
 */
class MongoTokenStore {
    /**
     * Save user tokens to MongoDB
     * @param userId - Clerk user ID
     * @param tokens - Token data to store
     */
    async saveTokens(userId: string, tokens: Omit<UserTokens, 'userId' | 'createdAt' | 'updatedAt'>): Promise<void> {
        try {
            // Encrypt sensitive tokens before storing
            const encryptedAccessToken = encrypt(tokens.accessToken);
            const encryptedRefreshToken = tokens.refreshToken ? encrypt(tokens.refreshToken) : null;

            // Upsert: update if exists, create if not
            await UserTokensModel.findOneAndUpdate(
                { userId },
                {
                    $set: {
                        accessToken: encryptedAccessToken,
                        refreshToken: encryptedRefreshToken,
                        expiryDate: tokens.expiryDate,
                        scope: tokens.scope,
                        tokenType: tokens.tokenType,
                    },
                },
                {
                    upsert: true,
                    new: true,
                }
            );

            console.log(`✅ Tokens saved for user: ${userId}`);
        } catch (error) {
            console.error('❌ Error saving tokens:', error);
            throw new Error('Failed to save tokens to database');
        }
    }

    /**
     * Retrieve user tokens from MongoDB
     * @param userId - Clerk user ID
     * @returns User tokens or null if not found
     */
    async getTokens(userId: string): Promise<UserTokens | null> {
        try {
            const doc = await UserTokensModel.findOne({ userId });

            if (!doc) {
                return null;
            }

            // Decrypt tokens before returning
            const decryptedAccessToken = decrypt(doc.accessToken);
            const decryptedRefreshToken = doc.refreshToken ? decrypt(doc.refreshToken) : null;

            return {
                userId: doc.userId,
                accessToken: decryptedAccessToken,
                refreshToken: decryptedRefreshToken,
                expiryDate: doc.expiryDate,
                scope: doc.scope,
                tokenType: doc.tokenType,
                createdAt: doc.createdAt,
                updatedAt: doc.updatedAt,
            };
        } catch (error) {
            console.error('❌ Error retrieving tokens:', error);
            throw new Error('Failed to retrieve tokens from database');
        }
    }

    /**
     * Update access token (after refresh)
     * @param userId - Clerk user ID
     * @param accessToken - New access token
     * @param expiryDate - New expiry date
     */
    async updateAccessToken(userId: string, accessToken: string, expiryDate: number): Promise<void> {
        try {
            const encryptedAccessToken = encrypt(accessToken);

            const result = await UserTokensModel.findOneAndUpdate(
                { userId },
                {
                    $set: {
                        accessToken: encryptedAccessToken,
                        expiryDate: expiryDate,
                    },
                },
                { new: true }
            );

            if (!result) {
                throw new Error(`No tokens found for user: ${userId}`);
            }

            console.log(`✅ Access token updated for user: ${userId}`);
        } catch (error) {
            console.error('❌ Error updating access token:', error);
            throw error;
        }
    }

    /**
     * Delete user tokens from MongoDB
     * @param userId - Clerk user ID
     * @returns True if tokens were deleted, false if not found
     */
    async deleteTokens(userId: string): Promise<boolean> {
        try {
            const result = await UserTokensModel.deleteOne({ userId });
            const deleted = result.deletedCount > 0;

            if (deleted) {
                console.log(`✅ Tokens deleted for user: ${userId}`);
            } else {
                console.log(`⚠️  No tokens found for user: ${userId}`);
            }

            return deleted;
        } catch (error) {
            console.error('❌ Error deleting tokens:', error);
            throw new Error('Failed to delete tokens from database');
        }
    }

    /**
     * Check if user has tokens stored
     * @param userId - Clerk user ID
     * @returns True if tokens exist
     */
    async hasTokens(userId: string): Promise<boolean> {
        try {
            const count = await UserTokensModel.countDocuments({ userId });
            return count > 0;
        } catch (error) {
            console.error('❌ Error checking tokens:', error);
            return false;
        }
    }

    /**
     * Clean up expired tokens (optional maintenance task)
     * Run this periodically via cron job
     */
    async cleanupExpiredTokens(): Promise<void> {
        try {
            const now = Date.now();
            const result = await UserTokensModel.deleteMany({
                expiryDate: { $lt: now },
                refreshToken: null, // Only delete if no refresh token (can't renew)
            });

            console.log(`🧹 Cleaned up ${result.deletedCount} expired tokens`);
        } catch (error) {
            console.error('❌ Error cleaning up expired tokens:', error);
        }
    }
}

// Export singleton instance
export const tokenStore = new MongoTokenStore();
