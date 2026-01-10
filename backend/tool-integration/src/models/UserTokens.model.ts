import mongoose, { Schema, Document } from 'mongoose';

/**
 * UserTokens document interface for MongoDB
 */
export interface IUserTokensDocument extends Document {
    userId: string;
    accessToken: string; // Encrypted
    refreshToken: string | null; // Encrypted
    expiryDate: number | null;
    scope?: string;
    tokenType?: string;
    createdAt: Date;
    updatedAt: Date;
}

/**
 * UserTokens Schema
 * Stores encrypted Google OAuth tokens linked to Clerk user IDs
 */
const UserTokensSchema = new Schema<IUserTokensDocument>(
    {
        userId: {
            type: String,
            required: true,
            unique: true,
            index: true,
        },
        accessToken: {
            type: String,
            required: true,
        },
        refreshToken: {
            type: String,
            default: null,
        },
        expiryDate: {
            type: Number,
            default: null,
        },
        scope: {
            type: String,
        },
        tokenType: {
            type: String,
        },
    },
    {
        timestamps: true, // Automatically adds createdAt and updatedAt
    }
);

// Create index for efficient queries
UserTokensSchema.index({ userId: 1 });
UserTokensSchema.index({ updatedAt: -1 });

// Create and export the model
export const UserTokensModel = mongoose.model<IUserTokensDocument>('UserTokens', UserTokensSchema);
