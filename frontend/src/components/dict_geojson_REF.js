const geojsonSlice = createSlice({
  name: 'geojson',
  initialState: {
    dep: null,
  },
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchMO.fulfilled, (state, action) => {
        state.dep = action.payload;
      })
  },
});

export default geojsonSlice.reducer;
