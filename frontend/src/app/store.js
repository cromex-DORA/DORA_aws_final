import { configureStore } from '@reduxjs/toolkit';
import geojsonReducer from '../features/geojson/geojsonSlice';

export const store = configureStore({
  reducer: {
    geojson: geojsonReducer,
  },
});
