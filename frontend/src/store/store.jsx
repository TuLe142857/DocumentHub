import { configureStore } from '@reduxjs/toolkit';
import userReducer from './slice/userSlice.jsx';

export default configureStore({
  reducer: {
    user: userReducer,
  },
});
