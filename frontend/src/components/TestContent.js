import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchMOThunk } from '../features/geojson/geojsonSlice';
import { MapContainer, TileLayer, GeoJSON } from 'react-leaflet';

const MapComponent = () => {
  const dispatch = useDispatch();
  const mo = useSelector((state) => {
    console.log("State in useSelector:", state.geojson.mo);  // Vérification des données
    return state.geojson.mo;
  });

  useEffect(() => {
    dispatch(fetchMOThunk());
  }, [dispatch]);

  return (
    <MapContainer style={{ height: '500px', width: '100%' }} center={[51.505, -0.09]} zoom={13}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {mo && <GeoJSON data={mo} />}
    </MapContainer>
  );
};


export default MapComponent;
