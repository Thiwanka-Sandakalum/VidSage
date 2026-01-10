/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
/**
 * Request model for RAG-based answer generation.
 */
export type GenerateRequest = {
    /**
     * User question to answer
     */
    query: string;
    /**
     * YouTube video ID to search in
     */
    video_id: string;
    /**
     * Number of context chunks to retrieve
     */
    top_k?: number;
    /**
     * Enable streaming responses
     */
    stream?: boolean;
};

