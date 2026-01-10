/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class StatsService {
    /**
     * Get system statistics
     * Get statistics about processed videos and embeddings
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getStatsStatsGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/stats',
            errors: {
                500: `Internal Server Error`,
            },
        });
    }
}
