import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import authApi from '@/api/authApi.js';

export const fetchUserInfo = createAsyncThunk(
  'auth/fetchUserInfo',
  async (_, thunkAPI) => {
    try {
      const response = await authApi.whoami();
      return response.data.data;
    } catch (error) {
      const msg = error.response?.data?.message || 'Something went wrong.';
      return thunkAPI.rejectWithValue(msg);
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
        // state.isAuthenticated = false;
        // state.user = null;
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
