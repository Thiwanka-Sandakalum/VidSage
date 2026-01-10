import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../services/api';
import { VideosService } from '../services';

interface SummaryState {
    summary: string;
    loading: boolean;
    error: string | null;
    sources: any[]; // Added sources to summary state
}

const initialState: SummaryState = {
    summary: '',
    loading: false,
    error: null,
    sources: [], // Initialize sources as an empty array
};

export const fetchVideoSummary = createAsyncThunk(
    'summary/fetch',
    async (videoId: string, { rejectWithValue }) => {
        try {
            const result = await VideosService.getVideoSummaryVideosVideoIdSummaryGet(videoId);
            return { summary: result.summary, sources: result.sources || [] };
        } catch (error: any) {
            return rejectWithValue(error.message || 'Failed to generate summary');
        }
    }
);

const summarySlice = createSlice({
    name: 'summary',
    initialState,
    reducers: {},
    extraReducers: (builder) => {
        builder
            .addCase(fetchVideoSummary.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(fetchVideoSummary.fulfilled, (state, action: PayloadAction<{ summary: string, sources: any[] }>) => {
                state.summary = action.payload.summary;
                state.sources = action.payload.sources;
                state.loading = false;
            })
            .addCase(fetchVideoSummary.rejected, (state, action) => {
                state.error = action.payload as string;
                state.loading = false;
            });
    },
});

export default summarySlice.reducer;
