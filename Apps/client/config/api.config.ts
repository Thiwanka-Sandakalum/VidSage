import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = (window as any).appConfig?.API_BASE_URL || 'http://localhost:8000';

export const apiClient: AxiosInstance = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000,
    headers: {
        'Content-Type': 'application/json',
    },
});


apiClient.interceptors.response.use(
    (response) => {
        return response;
    },
    (error: AxiosError) => {
        if (error.response) {
            const status = error.response.status;
            const data: any = error.response.data;

            switch (status) {
                case 400:
                    console.error('Bad Request:', data.detail || data.error);
                    break;
                case 404:
                    console.error('Not Found:', data.detail || data.error);
                    break;
                case 500:
                    console.error('Server Error:', data.detail || data.error);
                    break;
                default:
                    console.error('API Error:', data.detail || data.error || error.message);
            }
        } else if (error.request) {
            console.error('Network Error: No response from server');
        } else {
            console.error('Request Error:', error.message);
        }

        return Promise.reject(error);
    }
);

export default apiClient;
