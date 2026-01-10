"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.tokenStore = void 0;
const UserTokens_model_1 = require("../models/UserTokens.model");
const encryption_1 = require("../utils/encryption");
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
    async saveTokens(userId, tokens) {
        try {
            // Encrypt sensitive tokens before storing
            const encryptedAccessToken = (0, encryption_1.encrypt)(tokens.accessToken);
            const encryptedRefreshToken = tokens.refreshToken ? (0, encryption_1.encrypt)(tokens.refreshToken) : null;
            // Upsert: update if exists, create if not
            await UserTokens_model_1.UserTokensModel.findOneAndUpdate({ userId }, {
                $set: {
                    accessToken: encryptedAccessToken,
                    refreshToken: encryptedRefreshToken,
                    expiryDate: tokens.expiryDate,
                    scope: tokens.scope,
                    tokenType: tokens.tokenType,
                },
            }, {
                upsert: true,
                new: true,
            });
            console.log(`✅ Tokens saved for user: ${userId}`);
        }
        catch (error) {
            console.error('❌ Error saving tokens:', error);
            throw new Error('Failed to save tokens to database');
        }
    }
    /**
     * Retrieve user tokens from MongoDB
     * @param userId - Clerk user ID
     * @returns User tokens or null if not found
     */
    async getTokens(userId) {
        try {
            const doc = await UserTokens_model_1.UserTokensModel.findOne({ userId });
            if (!doc) {
                return null;
            }
            // Decrypt tokens before returning
            const decryptedAccessToken = (0, encryption_1.decrypt)(doc.accessToken);
            const decryptedRefreshToken = doc.refreshToken ? (0, encryption_1.decrypt)(doc.refreshToken) : null;
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
        }
        catch (error) {
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
    async updateAccessToken(userId, accessToken, expiryDate) {
        try {
            const encryptedAccessToken = (0, encryption_1.encrypt)(accessToken);
            const result = await UserTokens_model_1.UserTokensModel.findOneAndUpdate({ userId }, {
                $set: {
                    accessToken: encryptedAccessToken,
                    expiryDate: expiryDate,
                },
            }, { new: true });
            if (!result) {
                throw new Error(`No tokens found for user: ${userId}`);
            }
            console.log(`✅ Access token updated for user: ${userId}`);
        }
        catch (error) {
            console.error('❌ Error updating access token:', error);
            throw error;
        }
    }
    /**
     * Delete user tokens from MongoDB
     * @param userId - Clerk user ID
     * @returns True if tokens were deleted, false if not found
     */
    async deleteTokens(userId) {
        try {
            const result = await UserTokens_model_1.UserTokensModel.deleteOne({ userId });
            const deleted = result.deletedCount > 0;
            if (deleted) {
                console.log(`✅ Tokens deleted for user: ${userId}`);
            }
            else {
                console.log(`⚠️  No tokens found for user: ${userId}`);
            }
            return deleted;
        }
        catch (error) {
            console.error('❌ Error deleting tokens:', error);
            throw new Error('Failed to delete tokens from database');
        }
    }
    /**
     * Check if user has tokens stored
     * @param userId - Clerk user ID
     * @returns True if tokens exist
     */
    async hasTokens(userId) {
        try {
            const count = await UserTokens_model_1.UserTokensModel.countDocuments({ userId });
            return count > 0;
        }
        catch (error) {
            console.error('❌ Error checking tokens:', error);
            return false;
        }
    }
    /**
     * Clean up expired tokens (optional maintenance task)
     * Run this periodically via cron job
     */
    async cleanupExpiredTokens() {
        try {
            const now = Date.now();
            const result = await UserTokens_model_1.UserTokensModel.deleteMany({
                expiryDate: { $lt: now },
                refreshToken: null, // Only delete if no refresh token (can't renew)
            });
            console.log(`🧹 Cleaned up ${result.deletedCount} expired tokens`);
        }
        catch (error) {
            console.error('❌ Error cleaning up expired tokens:', error);
        }
    }
}
// Export singleton instance
exports.tokenStore = new MongoTokenStore();
//# sourceMappingURL=token.service.js.map