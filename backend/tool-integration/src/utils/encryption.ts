import CryptoJS from 'crypto-js';

const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY || 'vidsage-default-encryption-key-change-in-production';

/**
 * Encrypt sensitive data (tokens)
 * @param text - Plain text to encrypt
 * @returns Encrypted string
 */
export const encrypt = (text: string): string => {
    return CryptoJS.AES.encrypt(text, ENCRYPTION_KEY).toString();
};

/**
 * Decrypt sensitive data (tokens)
 * @param encryptedText - Encrypted string
 * @returns Decrypted plain text
 */
export const decrypt = (encryptedText: string): string => {
    const bytes = CryptoJS.AES.decrypt(encryptedText, ENCRYPTION_KEY);
    return bytes.toString(CryptoJS.enc.Utf8);
};

/**
 * Validate encryption key is set properly
 */
export const validateEncryptionKey = (): void => {
    if (ENCRYPTION_KEY === 'vidsage-default-encryption-key-change-in-production') {
        console.warn('⚠️  WARNING: Using default encryption key. Set ENCRYPTION_KEY in production!');
    }
};
