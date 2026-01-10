/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SourceChunk } from './SourceChunk';
/**
 * Response model for generated answers.
 */
export type GenerateResponse = {
    /**
     * Generated answer to the query
     */
    answer: string;
    /**
     * Source chunks used for answer
     */
    sources: Array<SourceChunk>;
    /**
     * LLM model used for generation
     */
    model: string;
};

