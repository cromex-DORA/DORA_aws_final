import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import L from 'leaflet'; // Pour accéder à l'objet global de Leaflet
import FiltretypeMO from './FiltretypeMO';
import FiltretypeSOUSREF from './FiltretypeSOUSREF';
import TabImportShpModal from './TabImportShpModal';
import 'leaflet/dist/leaflet.css';
import './MapDEPMOgemapi.css';
import { Button } from 'react-bootstrap';
import { useMapEvents } from 'react-leaflet';
import { useDispatch } from 'react-redux';
import { fetchMOThunk } from '../features/geojson/geojsonSlice';

const DEFAULT_LABEL_SIZE = 12;

// Composant pour ajuster la vue de la carte en fonction des limites
const ZoomToBounds = ({ bounds }) => {
    const map = useMap();

    useEffect(() => {
        if (bounds) {
            map.fitBounds(bounds);
        }
    }, [bounds, map]);

    return null;
};

// Composant pour gérer les événements de la carte
const MapEvents = ({ setZoomLevel }) => {
    useMapEvents({
        zoomend: (e) => {
            const zoom = e.target.getZoom();
            setZoomLevel(zoom);
        }
    });

    return null;
};



const MapDEPMOgemapi = ({ geoJsonData, setSelectedFolderId, selectedFolderId, highlightedFolderId, setHighlightedFolderId, handleFolderClick, handleMESelect }) => {
    const [filter, setFilter] = useState('Syndicat');
    const [selectedType, setSelectedType] = useState('ME');
    const [filteredGeoJsonData, setFilteredGeoJsonData] = useState(null);
    const [initialBounds, setInitialBounds] = useState(null);
    const [selectedBounds, setSelectedBounds] = useState(null);
    const [zoomLevel, setZoomLevel] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [highlightedMEId, setHighlightedMEId] = useState(null);
    const mapRef = useRef();
    const geoJsonLayerRefME = useRef();  // Référence pour ME
    const geoJsonLayerRefMO = useRef();  // Référence pour MO
    const [geoJsonKey, setGeoJsonKey] = useState(0);
    const geoJsonLayerRefPPG = useRef(); // Référence pour PPG
    const geoJsonLayerRefCEME = useRef(); // Référence pour CE_ME
    const selectedFolderIdRef = useRef(selectedFolderId);
    const [listeMEparMOselected, setListeMEparMOselected] = useState([]);
    const dispatch = useDispatch();
    const [labelSize, setLabelSize] = useState(DEFAULT_LABEL_SIZE);

    const handleFetchMO = () => {
        dispatch(fetchMOThunk()); // Dispatch l'action pour récupérer les données MO
    };


    useEffect(() => {
        if (geoJsonData) {
            const separatedData = {
                MO: geoJsonData.features.filter(feature => feature.properties['type_REF'] === 'MO')

            };
            setFilteredGeoJsonData(separatedData);
        }
    }, [geoJsonData]);


    useEffect(() => {
        selectedFolderIdRef.current = selectedFolderId; // Mets à jour la référence à chaque changement

        if (selectedFolderId) {
            const selectedMO = filteredGeoJsonData?.MO.find(mo => mo.id === selectedFolderId);

            if (selectedMO) {
                // Accéder aux coordonnées pour un MultiPolygon
                const coordinates = selectedMO.geometry.coordinates[0][0]; // Récupérer le premier polygone
          
                // Vérifie que les coordonnées sont bien définies
                const latLngs = coordinates.map(coord => {
                    const lat = coord[1];
                    const lon = coord[0];

                    // Vérifie que lat et lon ne sont pas NaN
                    if (isNaN(lat) || isNaN(lon)) {
                        console.error("Invalid coordinates:", coord);
                        return null; // Retourne null si les coordonnées sont invalides
                    }

                    return L.latLng(lat, lon);
                }).filter(Boolean); // Filtrer les valeurs null

                // Vérifie qu'il y a des coordonnées valides
                if (latLngs.length > 0) {
                    const bounds = L.latLngBounds(latLngs);
                    setSelectedBounds(bounds); // Mets à jour les bounds
                    setListeMEparMOselected(selectedMO.properties.liste_CODE_ME || []);
                } else {
                    console.error("No valid latLngs found.");
                }
            } else {
                setListeMEparMOselected([]); // Réinitialise si la MO sélectionnée n'est pas trouvée
            }
        } else {
            setListeMEparMOselected([]); // Réinitialise si aucun dossier n'est sélectionné
        }
    }, [selectedFolderId, filteredGeoJsonData]);





    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);

    // Fetch initial bounds on mount
    useEffect(() => {
        const fetchInitialBounds = async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                console.error("Token is missing");
                return;
            }

            try {
                const bboxResponse = await fetch(`${process.env.REACT_APP_IP_SERV}/bb_box`, {
                    headers: { 'Authorization': token }
                });

                if (!bboxResponse.ok) {
                    throw new Error(`HTTP error! Status: ${bboxResponse.status}`);
                }
                const bboxData = await bboxResponse.json();
                const bounds = [
                    [bboxData.miny, bboxData.minx],
                    [bboxData.maxy, bboxData.maxx]
                ];
                setInitialBounds(bounds);
            } catch (error) {
                console.error('Error fetching bounding box:', error);
            }
        };

        fetchInitialBounds();
    }, []);

    // Séparer les données GeoJSON par type_REF
    useEffect(() => {
        if (geoJsonData) {
            const separatedData = {
                MO: geoJsonData.features.filter(feature => feature.properties['type_REF'] === 'MO'),
                PPG: geoJsonData.features.filter(feature => feature.properties['type_REF'] === 'PPG'),
                ME: geoJsonData.features.filter(feature => feature.properties['type_REF'] === 'ME'),
                CE_ME: geoJsonData.features.filter(feature => feature.properties['type_REF'] === 'CE_ME')
            };
            setFilteredGeoJsonData(separatedData);
        }
    }, [geoJsonData]);


    useEffect(() => {
        if (geoJsonLayerRefMO.current && filteredGeoJsonData?.MO.length > 0) {
            geoJsonLayerRefMO.current.eachLayer(layer => {
                const feature = layer.feature;

                // Supprimer les tooltips existants
                layer.unbindTooltip();

                // Afficher ALIAS uniquement si le zoom est supérieur à un certain niveau
                if (!selectedFolderIdRef.current && zoomLevel >= 10) { // Par exemple, afficher à partir du niveau 10
                    layer.bindTooltip(labelMO(feature), {
                        permanent: true,
                        direction: "auto",
                        className: "mo-label"
                    });
                }
            });
        }
    }, [selectedFolderId, filteredGeoJsonData, zoomLevel]);


    useEffect(() => {
        if (geoJsonLayerRefME.current && filteredGeoJsonData?.ME.length > 0) {
            geoJsonLayerRefME.current.eachLayer(layer => {
                const feature = layer.feature;

                // Supprimer les tooltips existants
                layer.unbindTooltip();

                // Vérifie si la MO sélectionnée contient des coordonnées pour afficher les ME
                const selectedMO = filteredGeoJsonData.MO.find(mo => mo.id === selectedFolderIdRef.current);
                const meCoordinatesDict = selectedMO?.properties.dict_CODE_ME_et_coord || {};

                if (selectedFolderIdRef.current && listeMEparMOselected.includes(feature.id)) {
                    // Si les coordonnées sont définies pour cette ME, utilise-les pour l'affichage
                    const meCoordinates = meCoordinatesDict[feature.id];
                    const latLng = [parseFloat(meCoordinates[1]), parseFloat(meCoordinates[0])];

                    if (meCoordinates) {
                        // Créer le tooltip avec les coordonnées
                        layer.bindTooltip(labelME(feature), {
                            permanent: true,
                            direction: "center", // Ou "center" pour centrer
                            className: "small-tooltip",
                            offset: [0, 0] // Pas de décalage
                        });

                        // Utiliser setLatLng sur la couche pour définir la position
                        layer.getTooltip().setLatLng(latLng);
                    }
                }
            });
        }
    }, [selectedFolderIdRef.current, filteredGeoJsonData, listeMEparMOselected]);


    // labelMO and labelME functions
    const labelMO = (feature) => {
        return feature.properties.ALIAS; // Renvoie l'ALIAS ou un message par défaut
    };

    const labelME = (feature) => {
        return feature.properties.ALIAS; // Retourne le texte de l'étiquette pour ME
    };

    useEffect(() => {
        // Réappliquer le style aux couches MO et ME lors du changement de selectedFolderId
        if (geoJsonLayerRefMO.current) {
            geoJsonLayerRefMO.current.eachLayer((layer) => {
                layer.setStyle(style(layer.feature, highlightedFolderId, highlightedMEId, selectedFolderIdRef.current));
            });
        }

        if (geoJsonLayerRefME.current) {
            geoJsonLayerRefME.current.eachLayer((layer) => {
                layer.setStyle(style(layer.feature, highlightedFolderId, highlightedMEId, selectedFolderIdRef.current));
            });
        }
    }, [selectedFolderId, highlightedFolderId, highlightedMEId]); // Déclencher lorsque ces variables changent


    const onEachFeatureMO = (feature, layer) => {
        layer.on({
            click: () => {

                if (selectedFolderId === null) {

                    // Gérer le clic uniquement si aucun dossier n'est sélectionné

                    handleFolderClick({
                        id: feature.id,
                        name: feature.properties.NOM_MO,
                        path: feature.properties.path || '',
                        files: feature.properties.files || []
                    });

                    // Mettre à jour selectedFolderId
                    setSelectedFolderId(feature.id);
                    setHighlightedFolderId(null);
                }
            },
            mouseover: () => {
                if (selectedFolderIdRef.current == null) {
                    setHighlightedFolderId(feature.id);
                    layer.setStyle(style(feature, true)); // Applique le style de surbrillance
                }
            },
            mouseout: () => {
                if (selectedFolderIdRef.current == null) {
                    layer.setStyle(style(feature, false)); // Réapplique le style normal
                    setHighlightedFolderId(null);
                }
            }
        });
    };

    const onEachFeatureME = (feature, layer) => {
        layer.on({
            click: () => {
                if (selectedFolderIdRef.current !== null) {
                    // Mettre à jour l'état pour le ME sélectionné
                    handleMESelect(feature.id);
                }
            },
            mouseover: () => {
                if (selectedFolderIdRef.current) {
                    setHighlightedMEId(feature.id); // Met à jour avec l'ID de surlignage ME
                    layer.setStyle(style(feature, true)); // Applique le style de surbrillance
                }
            },
            mouseout: () => {
                if (selectedFolderIdRef.current) {
                    layer.setStyle(style(feature, false)); // Réapplique le style normal
                    setHighlightedMEId(null); // Réinitialise l'ID de surlignage ME
                }
            }
        });
    };


    const style = (feature, highlightedFolderId) => {
        const category = feature.properties['type_REF'];
        const isMOSelected = selectedFolderIdRef.current === feature.id;
        const isAnyMOSelected = selectedFolderId !== null;
        const featureId = feature.id; // Vérifiez que l'ID est correct

        // Vérifiez si l'entité MO doit être surlignée
        const isMOHighlighted = highlightedFolderId === featureId;
        const isMEHighlighted = highlightedMEId === featureId;

        if (isMOHighlighted) {
            return {
                color: 'yellow',
                weight: 5,
                fillOpacity: 0.6,
            };
        }

        if (isMEHighlighted) {
            return {
                color: 'yellow',
                fillColor: 'yellow', // Couleur pour ME surligné
                weight: 1,
                fillOpacity: 0.6,
            };
        }

        // Styles par défaut pour d'autres types
        if (category === 'MO') {
            if (isAnyMOSelected) {
                return {
                    color: isMOSelected ? 'green' : 'white', // Green pour le MO sélectionné, blanc pour les autres
                    weight: isMOSelected ? 4 : 1, // Weight de 6 pour le MO sélectionné, 2 pour les autres
                    fillColor: 'rgba(0, 255, 0, 0.1)',
                    fillOpacity: 0.1,
                    opacity: 1,
                    interactive: false
                };
            } else {
                return {
                    color: 'green', // Tous les MO sont verts si aucun n'est sélectionné
                    weight: 4, // Weight de 5 si aucun MO sélectionné
                    fillColor: 'rgba(0, 255, 0, 0.1)',
                    fillOpacity: 0.1,
                    opacity: 1,
                    interactive: true // Interactif si aucun n'est sélectionné
                };
            }
        }

        // Styles pour les ME
        if (category === 'ME') {
            if (isAnyMOSelected) {
                if (listeMEparMOselected.includes(featureId)) {
                    // Les ME dans la liste ont un weight de 4
                    return {
                        color: 'white',
                        fillColor: 'transparent',
                        weight: 4,
                        fillOpacity: 0.1,
                        interactive: true,
                    };
                } else {
                    // Les ME hors de la liste sont blanches avec weight 0.5
                    return {
                        color: 'gray',
                        fillColor: 'white',
                        weight: 0.5,
                        fillOpacity: 0.0,
                        interactive: true,
                    };
                }
            } else {
                // Toutes les ME sont grises avec weight 2 si aucun MO n'est sélectionné
                return {
                    color: 'gray',
                    fillColor: 'transparent',
                    weight: 1,
                    fillOpacity: 0.3,
                    interactive: true,
                };
            }
        }

        if (category === 'CE_ME') {
            return {
                color: 'blue',
                weight: 1,
                fillColor: 'rgba(0, 0, 255, 0.2)',
                fillOpacity: 0.4,
                opacity: 1,
            };
        }

        return {}; // Style par défaut
    };



    // Attendre que les initialBounds soient définis avant de rendre la carte
    if (!initialBounds) {
        return <div>Loading map...</div>;
    }

    return (
        <div className="map-container">
            <div className="sidebar">
                {/* Autres éléments de ton composant ici */}
                <FiltretypeMO selectedOption={filter} setSelectedtypeMO={setFilter} />
                <FiltretypeSOUSREF selectedOption={selectedType} setSelectedOption={setSelectedType} />

                <Button className="import-button" onClick={openModal}>
                    Importer des polygones manquants
                </Button>
                <TabImportShpModal
                    isOpen={isModalOpen}
                    onRequestClose={closeModal}
                    initialBounds={initialBounds}
                />
                <Button className="fetch-button" onClick={handleFetchMO}>
                    Fetch MO
                </Button> {/* Ajout du bouton Fetch MO */}
            </div>
            {/* Autres éléments de ton composant ici */}
            <MapContainer
                bounds={initialBounds}
                className="map"
                whenCreated={map => { mapRef.current = map; }}
            >
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    opacity={0.3} // Ajuster l'opacité ici
                />
                {/* Rendu des polygones par type */}

                {/* Render MO GeoJSON */}
                {filteredGeoJsonData?.MO.length > 0 && (
                    <GeoJSON
                        key={`mo-${geoJsonKey}-${filteredGeoJsonData.MO.map(feature => feature.id).join('-')}-${selectedFolderId || 'none'}`} // Utilisation de geoJsonKey
                        data={filteredGeoJsonData.MO}
                        ref={geoJsonLayerRefMO}
                        onEachFeature={(feature, layer) => onEachFeatureMO(feature, layer)}
                        style={(feature) => style(feature, highlightedFolderId, highlightedMEId, selectedFolderIdRef.current)}
                    />
                )}

                {/* Render ME GeoJSON */}
                {filteredGeoJsonData?.ME.length > 0 && (
                    <GeoJSON
                        data={filteredGeoJsonData.ME}
                        ref={geoJsonLayerRefME}
                        onEachFeature={(feature, layer) => onEachFeatureME(feature, layer)}
                        style={style}
                    />
                )}

                {/* Render CE_ME GeoJSON */}
                {filteredGeoJsonData?.CE_ME.length > 0 && (
                    <GeoJSON
                        key={`ceme-${filteredGeoJsonData.CE_ME.length}`}
                        data={filteredGeoJsonData.CE_ME}
                        ref={geoJsonLayerRefCEME}

                        style={(feature) => style(feature, false)}
                    />
                )}
                {selectedBounds && <ZoomToBounds bounds={selectedBounds} />}
                <MapEvents setZoomLevel={setZoomLevel} />
            </MapContainer>
        </div>
    );
};

export default MapDEPMOgemapi;
