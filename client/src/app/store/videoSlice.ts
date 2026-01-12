import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../../services/api';
import { ProcessStatus, VideoMetadata, VideoState } from '../../types/types';

const initialState: VideoState = {
  currentVideo: null,
  transcript: '',
  summary: '',
  suggestedQuestions: [],
  status: ProcessStatus.IDLE,
  progress: 0,
  error: null,
  history: [],
  stats: null
};

export const fetchStats = createAsyncThunk('video/fetchStats', async () => {
  return await api.getStats();
});

export const fetchHistory = createAsyncThunk('video/fetchHistory', async () => {
  return await api.listVideos();
});

export const processVideo = createAsyncThunk(
  'video/process',
  async (videoUrl: string, { dispatch, rejectWithValue }) => {
    try {
      // Step 1: Metadata Extraction
      dispatch(updateStatus({ status: ProcessStatus.EXTRACTING, progress: 25 }));
      await new Promise(r => setTimeout(r, 1500)); // Visual delay for realism

      // Step 2: Transcription / Chunking
      dispatch(updateStatus({ status: ProcessStatus.TRANSCRIBING, progress: 50 }));
      await new Promise(r => setTimeout(r, 2000));

      // Step 3: Vectorization / Analysis
      dispatch(updateStatus({ status: ProcessStatus.ANALYZING, progress: 75 }));

      const result = await api.processVideo(videoUrl);

      // Step 4: Finalizing
      dispatch(updateStatus({ status: ProcessStatus.COMPLETED, progress: 100 }));
      await new Promise(r => setTimeout(r, 1000));

      return result;
    } catch (error: any) {
      return rejectWithValue(error.message || "Failed to process video");
    }
  }
);

export const deleteVideo = createAsyncThunk('video/delete', async (videoId: string, { dispatch }) => {
  await api.deleteVideo(videoId);
  dispatch(fetchHistory());
  return videoId;
});

export const fetchSuggestedQuestions = createAsyncThunk('video/fetchSuggestions', async (videoId: string) => {
  return await api.getSuggestions(videoId);
});

const videoSlice = createSlice({
  name: 'video',
  initialState,
  reducers: {
    updateStatus: (state, action: PayloadAction<{ status: ProcessStatus; progress: number }>) => {
      state.status = action.payload.status;
      state.progress = action.payload.progress;
    },
    resetVideoState: (state) => {
      state.currentVideo = null;
      state.status = ProcessStatus.IDLE;
      state.progress = 0;
      state.summary = '';
      state.transcript = '';
      state.error = null;
      state.suggestedQuestions = [];
    },
    selectVideoFromHistory: (state, action: PayloadAction<VideoMetadata>) => {
      state.currentVideo = action.payload;
      state.status = ProcessStatus.COMPLETED;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(processVideo.fulfilled, (state, action) => {
        state.currentVideo = action.payload.video;
        state.transcript = action.payload.transcript;
        state.summary = action.payload.summary;
        state.suggestedQuestions = action.payload.questions;
        state.status = ProcessStatus.IDLE; // Reset to idle for next use
      })
      .addCase(processVideo.rejected, (state, action) => {
        state.status = ProcessStatus.FAILED;
        state.error = action.payload as string;
      })
      .addCase(fetchHistory.fulfilled, (state, action) => {
        state.history = action.payload;
      })
      .addCase(fetchStats.fulfilled, (state, action) => {
        state.stats = action.payload;
      })
      .addCase(deleteVideo.fulfilled, (state, action) => {
        if (state.currentVideo?.id === action.payload) {
          state.currentVideo = null;
        }
      })
      .addCase(fetchSuggestedQuestions.fulfilled, (state, action) => {
        state.suggestedQuestions = action.payload;
      });
  },
});

export const { updateStatus, resetVideoState, selectVideoFromHistory } = videoSlice.actions;
export default videoSlice.reducer;
