/**
 * Encrypt sensitive data (tokens)
 * @param text - Plain text to encrypt
 * @returns Encrypted string
 */
export declare const encrypt: (text: string) => string;
/**
 * Decrypt sensitive data (tokens)
 * @param encryptedText - Encrypted string
 * @returns Decrypted plain text
 */
export declare const decrypt: (encryptedText: string) => string;
/**
 * Validate encryption key is set properly
 */
export declare const validateEncryptionKey: () => void;
//# sourceMappingURL=encryption.d.ts.map