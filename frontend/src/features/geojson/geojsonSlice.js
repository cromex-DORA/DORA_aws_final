import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { fetchGeoJSON } from '../../api/geojsonAPI';

// Thunks pour chaque type de données
export const fetchDEPThunk = createAsyncThunk('geojson/fetchDEP', async () => {
  return await fetchGeoJSON('DEP');
});

export const fetchCTThunk = createAsyncThunk('geojson/fetchCT', async () => {
  return await fetchGeoJSON('CT');
});

export const fetchEPTBThunk = createAsyncThunk('geojson/fetchEPTB', async () => {
  return await fetchGeoJSON('EPTB');
});

export const fetchSAGEThunk = createAsyncThunk('geojson/fetchSAGE', async () => {
  return await fetchGeoJSON('SAGE');
});

export const fetchMOThunk = createAsyncThunk('geojson/fetchMO', async () => {
  return await fetchGeoJSON('MO');
});

export const fetchPPGThunk = createAsyncThunk('geojson/fetchPPG', async () => {
  return await fetchGeoJSON('PPG');
});

export const fetchBVGThunk = createAsyncThunk('geojson/fetchBVG', async () => {
  return await fetchGeoJSON('BVG');
});

export const fetchMEThunk = createAsyncThunk('geojson/fetchME', async () => {
  return await fetchGeoJSON('ME');
});

export const fetchSMEThunk = createAsyncThunk('geojson/fetchSME', async () => {
  return await fetchGeoJSON('SME');
});

export const fetchROEThunk = createAsyncThunk('geojson/fetchROE', async () => {
  return await fetchGeoJSON('ROE');
});
export const fetchCEMEThunk = createAsyncThunk('geojson/fetchCE_ME', async () => {
  return await fetchGeoJSON('CE_ME');
});

// Slice pour gérer les états des données GeoJSON
const geojsonSlice = createSlice({
  name: 'geojson',
  initialState: {
    dep: null,
    ct: null,
    eptb: null,
    sage: null,
    mo: null,
    ppg: null,
    bvg: null,
    me: null,
    sme: null,
    roe: null,
    ceme: null,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchDEPThunk.fulfilled, (state, action) => {
        state.dep = action.payload;
      })
      .addCase(fetchCTThunk.fulfilled, (state, action) => {
        state.ct = action.payload;
      })
      .addCase(fetchEPTBThunk.fulfilled, (state, action) => {
        state.eptb = action.payload;
      })
      .addCase(fetchSAGEThunk.fulfilled, (state, action) => {
        state.sage = action.payload;
      })
      .addCase(fetchMOThunk.fulfilled, (state, action) => {
        state.mo = action.payload;
      })
      .addCase(fetchPPGThunk.fulfilled, (state, action) => {
        state.ppg = action.payload;
      })
      .addCase(fetchBVGThunk.fulfilled, (state, action) => {
        state.bvg = action.payload;
      })
      .addCase(fetchMEThunk.fulfilled, (state, action) => {
        state.me = action.payload;
      })
      .addCase(fetchSMEThunk.fulfilled, (state, action) => {
        state.sme = action.payload;
      })
      .addCase(fetchROEThunk.fulfilled, (state, action) => {
        state.roe = action.payload;
      })
      .addCase(fetchCEMEThunk.fulfilled, (state, action) => {
        state.ceme = action.payload;
      })      
      .addMatcher(action => action.type.endsWith('/rejected'), (state, action) => {
        state.error = action.error.message;
        console.error("Fetching failed:", action.error.message);
      });
  },
});

export default geojsonSlice.reducer;
