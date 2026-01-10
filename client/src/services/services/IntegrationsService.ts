/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class IntegrationsService {
    /**
     * Initialize Google OAuth
     * Start Google OAuth flow for account integration
     * @returns any Successful Response
     * @throws ApiError
     */
    public static googleAuthInitIntegrationsGoogleAuthGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/integrations/google/auth',
            errors: {
                400: `Bad Request`,
                500: `Internal Server Error`,
            },
        });
    }
    /**
     * Check Google OAuth status
     * Check if user has connected their Google account
     * @returns any Successful Response
     * @throws ApiError
     */
    public static googleAuthStatusIntegrationsGoogleStatusGet(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/integrations/google/status',
            errors: {
                401: `Unauthorized`,
                500: `Internal Server Error`,
            },
        });
    }
    /**
     * Disconnect Google account
     * Revoke Google OAuth access and delete stored tokens
     * @returns any Successful Response
     * @throws ApiError
     */
    public static googleDisconnectIntegrationsGoogleDisconnectDelete(): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/integrations/google/disconnect',
            errors: {
                401: `Unauthorized`,
                404: `Not Connected`,
                500: `Internal Server Error`,
            },
        });
    }
}
