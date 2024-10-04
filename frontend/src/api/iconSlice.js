import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

// Thunk pour récupérer le dictionnaire d'icônes
export const fetchIconsThunk = createAsyncThunk('icons/fetchIcons', async () => {
  const response = await fetch(`${process.env.REACT_APP_IP_SERV}/api/icons_DORA`)
  if (!response.ok) {
    throw new Error('Failed to fetch icons');
  }
  return await response.json(); // On récupère les données sous forme de JSON
});

// Slice pour gérer les icônes
const iconSlice = createSlice({
  name: 'icons',
  initialState: {
    icons: {},
    loading: false,
    error: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchIconsThunk.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchIconsThunk.fulfilled, (state, action) => {
        state.loading = false;
        state.icons = action.payload; // Stocke les icônes dans le store
      })
      .addCase(fetchIconsThunk.rejected, (state, action) => {
        state.loading = false;
        state.error = action.error.message;
      });
  },
});

export default iconSlice.reducer;
