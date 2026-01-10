/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_save_video_api_v1_videos_save_post } from '../models/Body_save_video_api_v1_videos_save_post';
import type { ListVideosResponse } from '../models/ListVideosResponse';
import type { ProcessVideoRequest } from '../models/ProcessVideoRequest';
import type { ProcessVideoResponse } from '../models/ProcessVideoResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class VideosService {
    /**
     * Process a YouTube video
     * Extract transcript, create embeddings, and store in database
     * @param requestBody
     * @returns ProcessVideoResponse Successful Response
     * @throws ApiError
     */
    public static processVideoApiV1VideosProcessPost(
        requestBody: ProcessVideoRequest,
    ): CancelablePromise<ProcessVideoResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/videos/process',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                400: `Bad Request`,
                401: `Unauthorized`,
                422: `Validation Error`,
                500: `Internal Server Error`,
            },
        });
    }
    /**
     * List user's videos
     * Get all videos processed by the current user
     * @returns ListVideosResponse Successful Response
     * @throws ApiError
     */
    public static listVideosApiV1VideosGet(): CancelablePromise<ListVideosResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/v1/videos',
            errors: {
                401: `Unauthorized`,
                500: `Internal Server Error`,
            },
        });
    }
    /**
     * Save video to library
     * Add a video to user's library
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public static saveVideoApiV1VideosSavePost(
        requestBody: Body_save_video_api_v1_videos_save_post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/v1/videos/save',
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
