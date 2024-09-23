import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchPPGThunk } from '../features/geojson/geojsonSlice';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';

const MapComponent = () => {
  const dispatch = useDispatch();
  const ppg = useSelector((state) => {
    console.log("State in useSelector:", state.geojson.ppg);  // Vérification des données
    return state.geojson.ppg;
  });

  useEffect(() => {
    dispatch(fetchPPGThunk());
  }, [dispatch]);

  return (
    <MapContainer style={{ height: '500px', width: '100%' }} center={[51.505, -0.09]} zoom={13}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {ppg && <GeoJSON data={ppg} />}
    </MapContainer>
  );
};


export default MapComponent;
