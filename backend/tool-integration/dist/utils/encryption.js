"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateEncryptionKey = exports.decrypt = exports.encrypt = void 0;
const crypto_js_1 = __importDefault(require("crypto-js"));
const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY || 'vidsage-default-encryption-key-change-in-production';
/**
 * Encrypt sensitive data (tokens)
 * @param text - Plain text to encrypt
 * @returns Encrypted string
 */
const encrypt = (text) => {
    return crypto_js_1.default.AES.encrypt(text, ENCRYPTION_KEY).toString();
};
exports.encrypt = encrypt;
/**
 * Decrypt sensitive data (tokens)
 * @param encryptedText - Encrypted string
 * @returns Decrypted plain text
 */
const decrypt = (encryptedText) => {
    const bytes = crypto_js_1.default.AES.decrypt(encryptedText, ENCRYPTION_KEY);
    return bytes.toString(crypto_js_1.default.enc.Utf8);
};
exports.decrypt = decrypt;
/**
 * Validate encryption key is set properly
 */
const validateEncryptionKey = () => {
    if (ENCRYPTION_KEY === 'vidsage-default-encryption-key-change-in-production') {
        console.warn('⚠️  WARNING: Using default encryption key. Set ENCRYPTION_KEY in production!');
    }
};
exports.validateEncryptionKey = validateEncryptionKey;
//# sourceMappingURL=encryption.js.map