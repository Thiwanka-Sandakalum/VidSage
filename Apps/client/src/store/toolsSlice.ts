
import { createSlice, PayloadAction, createAsyncThunk } from '@reduxjs/toolkit';
import { ToolsState } from '../types/types';
import { api } from '../services/api';

const initialState: ToolsState = {
  integrations: [
    {
      id: 'google-docs',
      name: 'Google Docs',
      description: 'Automatically sync video summaries and chat notes to your Google Docs account.',
      icon: 'fas fa-file-alt',
      isConnected: false,
      color: 'blue',
    },
    {
      id: 'notion',
      name: 'Notion',
      description: 'Export structured video research and transcripts directly to Notion databases.',
      icon: 'fas fa-book-open',
      isConnected: false,
      color: 'dark',
    }
  ],
  loading: false,
  error: null,
};

// Async thunks
export const checkGoogleStatus = createAsyncThunk(
  'tools/checkGoogleStatus',
  async () => {
    const status = await api.getGoogleStatus();
    return status;
  }
);

export const connectGoogle = createAsyncThunk(
  'tools/connectGoogle',
  async () => {
    await api.connectGoogle();
  }
);

export const disconnectGoogle = createAsyncThunk(
  'tools/disconnectGoogle',
  async () => {
    await api.disconnectGoogle();
  }
);

const toolsSlice = createSlice({
  name: 'tools',
  initialState,
  reducers: {
    toggleConnection: (state, action: PayloadAction<string>) => {
      const tool = state.integrations.find(t => t.id === action.payload);
      if (tool) {
        tool.isConnected = !tool.isConnected;
      }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(checkGoogleStatus.pending, (state) => {
        state.loading = true;
      })
      .addCase(checkGoogleStatus.fulfilled, (state, action) => {
        state.loading = false;
        const googleDocs = state.integrations.find(t => t.id === 'google-docs');
        // Use 'authorized' property from the response
        const isAuthorized = action.payload.authorized || false;
        if (googleDocs) googleDocs.isConnected = isAuthorized;
      })
      .addCase(checkGoogleStatus.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message || 'Failed to check status';
      })
      .addCase(disconnectGoogle.fulfilled, (state) => {
        const googleDocs = state.integrations.find(t => t.id === 'google-docs');
        if (googleDocs) googleDocs.isConnected = false;
      });
  },
});

export const { toggleConnection } = toolsSlice.actions;
export default toolsSlice.reducer;
