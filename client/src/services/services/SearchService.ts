/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SearchRequest } from '../models/SearchRequest';
import type { SearchResponse } from '../models/SearchResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class SearchService {
    /**
     * Search video content
     * Perform semantic search within a video's transcript
     * @param requestBody
     * @returns SearchResponse Successful Response
     * @throws ApiError
     */
    public static searchVideoSearchPost(
        requestBody: SearchRequest,
    ): CancelablePromise<SearchResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/search',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                401: `Unauthorized`,
                404: `Video Not Found`,
                422: `Validation Error`,
                500: `Internal Server Error`,
            },
        });
    }
}
