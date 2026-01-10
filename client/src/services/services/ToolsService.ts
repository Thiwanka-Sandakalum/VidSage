/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { SaveSummaryRequest } from '../models/SaveSummaryRequest';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ToolsService {
    /**
     * Save video summary to Google Doc
     * Fetches the video summary and saves it as a new Google Doc via the tool API.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static saveSummaryToDocToolsSaveSummaryToDocPost(
        requestBody: SaveSummaryRequest,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/tools/save-summary-to-doc',
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
    /**
     * Check if video summary is saved to Google Doc
     * Checks if a Google Doc for the video summary already exists for the user.
     * @param videoId Video ID to check
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getSummaryDocLinkToolsSummaryDocLinkGet(
        videoId: string,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/tools/summary-doc-link',
            query: {
                'video_id': videoId,
            },
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
