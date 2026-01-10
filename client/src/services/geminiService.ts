/**
 * Gemini Service
 * Provides text-to-speech and other AI features
 */


interface GeminiService {
    /**
     * Convert text to speech using Gemini TTS API
     * @param text The text to convert to speech
     * @param options Optional config: voiceName, apiKey, model
     */
    textToSpeech: (text: string, options?: {
        voiceName?: string;
        model?: string;
    }) => Promise<ArrayBuffer>;
}


export const geminiService: GeminiService = {
    /**
     * Convert text to speech using Gemini TTS API (single speaker)
     * @param text The text to convert
     * @param options Optional: { voiceName, apiKey, model }
     * @returns ArrayBuffer of PCM audio (24kHz, mono, 16-bit signed)
     */
    async textToSpeech(text: string, options?: {
        voiceName?: string;
        model?: string;
    }): Promise<ArrayBuffer> {
        const apiKey = (window as any).config.GEMINI_API_KEY;
        if (!apiKey) throw new Error('Gemini API key is required.');
        const model = options?.model || 'gemini-2.5-flash-preview-tts';
        const voiceName = options?.voiceName || 'Kore';

        const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;
        const body = {
            contents: [{
                parts: [{ text }]
            }],
            generationConfig: {
                responseModalities: ["AUDIO"],
                speechConfig: {
                    voiceConfig: {
                        prebuiltVoiceConfig: {
                            voiceName
                        }
                    }
                }
            },
            model
        };

        const res = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-goog-api-key': apiKey
            },
            body: JSON.stringify(body)
        });
        if (!res.ok) {
            const err = await res.text();
            throw new Error(`Gemini TTS API error: ${res.status} ${err}`);
        }
        const data = await res.json();
        // Path: candidates[0].content.parts[0].inlineData.data (base64 PCM)
        const base64 = data?.candidates?.[0]?.content?.parts?.[0]?.inlineData?.data;
        if (!base64) throw new Error('No audio data returned from Gemini TTS API.');
        // Convert base64 to ArrayBuffer
        const binary = atob(base64);
        const buf = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
            buf[i] = binary.charCodeAt(i);
        }
        return buf.buffer;
    }
};

export default geminiService;
