import { configureStore } from '@reduxjs/toolkit';
import geojsonReducer from '../features/geojson/geojsonSlice';
import iconReducer from '../api/iconSlice';

export const store = configureStore({
  reducer: {
    geojson: geojsonReducer,
    icons: iconReducer,
  },
});
