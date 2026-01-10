/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SuggestionsResponse } from '../models/SuggestionsResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SuggestionsService {
    /**
     * Get suggested questions
     * Get AI-generated questions about a video
     * @param videoId
     * @returns SuggestionsResponse Successful Response
     * @throws ApiError
     */
    public static getSuggestionsApiV1SuggestionsVideoIdGet(
        videoId: string,
    ): CancelablePromise<SuggestionsResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/suggestions/{video_id}',
            path: {
                'video_id': videoId,
            },
            errors: {
                404: `Video Not Found`,
                422: `Validation Error`,
                500: `Internal Server Error`,
            },
        });
    }
}
