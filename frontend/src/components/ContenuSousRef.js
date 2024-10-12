import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { fetchIconsThunk } from '../api/iconSlice'; // Assure-toi que le thunk est bien défini

const ContenuSousRef = ({ selectedMEId }) => {
  const dispatch = useDispatch();
  const icons = useSelector((state) => state.icons.icons); // Dictionnaire global des icônes
  const loading = useSelector((state) => state.icons.loading);
  const error = useSelector((state) => state.icons.error);
  const [meIcons, setMeIcons] = React.useState({ pressionSignificative: [], pressionNonSignificative: [] });

  useEffect(() => {
    dispatch(fetchIconsThunk()); // Appel du thunk pour récupérer toutes les icônes

    // Interroger le backend pour récupérer les icônes spécifiques au ME sélectionné
    const fetchMEIcons = async () => {
      if (selectedMEId) {
        try {
          const response = await fetch(`${process.env.REACT_APP_IP_SERV}/api/me_icons/${selectedMEId}`);
          if (!response.ok) {
            throw new Error('Failed to fetch ME icons');
          }
          const data = await response.json();
          setMeIcons(data); // Stocke les icônes spécifiques au ME dans l'état local
        } catch (error) {
          console.error(error);
        }
      }
    };

    fetchMEIcons();
  }, [dispatch, selectedMEId]);

  const handleIconClick = (iconName) => {
    console.log(`Icône ${iconName} cliquée !`);
    // Actions supplémentaires si besoin
  };

  if (loading) return <p>Loading icons...</p>;
  if (error) return <p>Error loading icons: {error}</p>;

  return (
    <div>
      <h1>Contenu Sous Ref - Icônes basées sur ME ID</h1>
      <h4>ID de ME sélectionnée: {selectedMEId !== null ? selectedMEId : 'Aucune'}</h4>

      {/* Pression significative */}
      <h3>Pression significative</h3>
      <div style={{ border: '2px solid red', padding: '10px', display: 'inline-block' }}>
        <table>
          <tbody>
            <tr>
              {meIcons.pressionSignificative.map((icon, index) => (
                <td key={index} onClick={() => handleIconClick(icon.name)} style={{ cursor: 'pointer' }}>
                  <img src={icons[icon.name]} alt={`Icône ${icon.name}`} style={{ width: '50px', height: '50px' }} />
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>

      {/* Pression non-significative */}
      <h3>Pression non-significative</h3>
      <div style={{ border: '2px solid yellow', padding: '10px', display: 'inline-block' }}>
        <table>
          <tbody>
            <tr>
              {meIcons.pressionNonSignificative.map((icon, index) => (
                <td key={index} onClick={() => handleIconClick(icon.name)} style={{ cursor: 'pointer' }}>
                  <img src={icons[icon.name]} alt={`Icône ${icon.name}`} style={{ width: '50px', height: '50px' }} />
                </td>
              ))}
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ContenuSousRef;
