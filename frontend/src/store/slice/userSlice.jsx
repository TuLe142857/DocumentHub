import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import api from '@/api/api.js';

export const fetchUserInfo = createAsyncThunk(
  'auth/fetchUserInfo',
  async (_, thunkAPI) => {
    try {
      const response = await api.get('auth/whoami');
      return response.data.data;
    } catch (error) {
      thunkAPI.rejectWithValue(
        error?.response?.data?.message || 'Something went wrong'
      );
    }
  }
);

export const userSlice = createSlice({
  name: 'user',
  initialState: {
    isLoading: true,
    isAuthenticated: false,
    user: null,
  },
  reducers: {
    login: (state, action) => {
      state.isLoading = false;
      state.isAuthenticated = true;
      state.user = action.payload;
    },
    logout: (state) => {
      state.isLoading = false;
      state.isAuthenticated = false;
      state.user = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUserInfo.pending, (state) => {
        state.isLoading = true;
        state.isAuthenticated = false;
        state.user = null;
      })
      .addCase(fetchUserInfo.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload;
      })
      .addCase(fetchUserInfo.rejected, (state) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.user = null;
      });
  },
});
export const { login, logout } = userSlice.actions;
export default userSlice.reducer;
