import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { AuthState, User } from '../../types/types';

const initialState: AuthState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
};

const delay = (ms: number) => new Promise(res => setTimeout(res, ms));

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: { email: string; password?: string }, { rejectWithValue }) => {
    try {
      await delay(1000); // Simulate API latency
      const mockUser: User = {
        id: 'u123',
        name: credentials.email.split('@')[0],
        email: credentials.email,
        avatar: `https://api.dicebear.com/7.x/avataaars/svg?seed=${credentials.email}`,
      };
      localStorage.setItem('vidsage_token', 'mock_token');
      return mockUser;
    } catch (error: any) {
      return rejectWithValue('Invalid credentials');
    }
  }
);

export const logout = createAsyncThunk(
  'auth/logout',
  async () => {
    await delay(500);
    localStorage.removeItem('vidsage_token');
    return null;
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    checkAuth: (state) => {
      const token = localStorage.getItem('vidsage_token');
      if (token) {
        state.isAuthenticated = true;
        // In a real app, we'd fetch user info with the token
        state.user = {
          id: 'u123',
          name: 'Demo User',
          email: 'demo@vidsage.ai',
          avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=demo',
        };
      }
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action: PayloadAction<User>) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.isAuthenticated = false;
      });
  },
});

export const { checkAuth } = authSlice.actions;
export default authSlice.reducer;
