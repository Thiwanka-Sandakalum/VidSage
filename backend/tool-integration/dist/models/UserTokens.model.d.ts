import mongoose, { Document } from 'mongoose';
/**
 * UserTokens document interface for MongoDB
 */
export interface IUserTokensDocument extends Document {
    userId: string;
    accessToken: string;
    refreshToken: string | null;
    expiryDate: number | null;
    scope?: string;
    tokenType?: string;
    createdAt: Date;
    updatedAt: Date;
}
export declare const UserTokensModel: mongoose.Model<IUserTokensDocument, {}, {}, {}, mongoose.Document<unknown, {}, IUserTokensDocument, {}, {}> & IUserTokensDocument & Required<{
    _id: mongoose.Types.ObjectId;
}> & {
    __v: number;
}, any>;
//# sourceMappingURL=UserTokens.model.d.ts.map