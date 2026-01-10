/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { GenerateRequest } from '../models/GenerateRequest';
import type { GenerateResponse } from '../models/GenerateResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class GenerateService {
    /**
     * Generate AI answer
     * Generate an AI-powered answer using RAG (Retrieval-Augmented Generation)
     * @param requestBody
     * @returns GenerateResponse Successful Response
     * @throws ApiError
     */
    public static generateAnswerApiV1GeneratePost(
        requestBody: GenerateRequest,
    ): CancelablePromise<GenerateResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/generate',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Unauthorized`,
                403: `Forbidden`,
                404: `Video Not Found`,
                422: `Validation Error`,
                500: `Internal Server Error`,
            },
        });
    }
}
