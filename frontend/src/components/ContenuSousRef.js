import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchIconsThunk } from '../api/iconSlice';

const ContenuSousRef = ({selectedMEId}) => {
  const dispatch = useDispatch();
  const icons = useSelector((state) => state.icons.icons);
  const loading = useSelector((state) => state.icons.loading);
  const error = useSelector((state) => state.icons.error);

  useEffect(() => {
    dispatch(fetchIconsThunk());  // Appel du thunk pour récupérer les icônes
  }, [dispatch]);

  if (loading) return <p>Loading icons...</p>;
  if (error) return <p>Error loading icons: {error}</p>;

  return (
    <div>
    <h1>Contenu Sous Ref - Test Icône MIA</h1>
    <h4>ID de ME sélectionnée: {selectedMEId !== null ? selectedMEId : 'Aucune'}</h4>
    <img src={icons.MIA_PRESS_ASS} alt="MIA Icon" style={{ width: '50px', height: '50px' }} />
    {/* Ajoute d'autres icônes ici selon le dict récupéré */}
    </div>
  );
};

export default ContenuSousRef;
