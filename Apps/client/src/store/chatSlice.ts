
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { api } from '../services/api';
import { ChatState } from '../types/types';

const initialState: ChatState = {
  messages: [],
  isLoading: false,
  error: null,
};

export const sendMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ message, videoId, transcript }: { message: string, videoId: string, transcript: string }, { rejectWithValue }) => {
    try {
      const result = await api.generateAnswer(message, videoId, transcript);
      return result;
    } catch (error: any) {
      return rejectWithValue(error.message || "Something went wrong while reaching the AI.");
    }
  }
);

const chatSlice = createSlice({
  name: 'chat',
  initialState,
  reducers: {
    addUserMessage: (state, action: PayloadAction<string>) => {
      state.messages.push({
        id: Date.now().toString(),
        role: 'user',
        content: action.payload,
        timestamp: Date.now(),
      });
      state.error = null; // Clear error when user sends a new message
    },
    clearChat: (state) => {
      state.messages = [];
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendMessage.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        state.isLoading = false;
        state.messages.push({
          id: Date.now().toString(),
          role: 'assistant',
          content: action.payload.answer,
          timestamp: Date.now(),
          sources: action.payload.sources
        });
      })
      .addCase(sendMessage.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { addUserMessage, clearChat } = chatSlice.actions;
export default chatSlice.reducer;
