/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { Body_save_video_videos_save_post } from '../models/Body_save_video_videos_save_post';
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
    public static processVideoVideosProcessPost(
        requestBody: ProcessVideoRequest,
    ): CancelablePromise<ProcessVideoResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/videos/process',
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
    public static listVideosVideosGet(): CancelablePromise<ListVideosResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/videos',
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
    public static saveVideoVideosSavePost(
        requestBody: Body_save_video_videos_save_post,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/videos/save',
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
    /**
     * Delete a video and its chunks
     * Delete a video and all its chunks from the database for the current user.
     * @param videoId YouTube video ID to delete
     * @returns any Successful Response
     * @throws ApiError
     */
    public static deleteVideoVideosVideoIdDelete(
        videoId: string,
    ): CancelablePromise<any> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/videos/{video_id}',
            path: {
                'video_id': videoId,
            },
            errors: {
                401: `Unauthorized`,
                404: `Video Not Found`,
                422: `Validation Error`,
                500: `Internal Server Error`,
            },
        });
    }
    /**
     * Get video summary
     * Retrieve the pre-generated summary for a processed video.
     * @param videoId
     * @returns any Successful Response
     * @throws ApiError
     */
    public static getVideoSummaryVideosVideoIdSummaryGet(
        videoId: string,
    ): CancelablePromise<Record<string, any>> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/videos/{video_id}/summary',
            path: {
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
