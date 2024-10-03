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
            console.log("niveau zoom:", zoom);
        }
    });

    return null;
};



const MapDEPMOgemapi = ({ geoJsonData, setSelectedFolderId, selectedFolderId, highlightedFolderId, setHighlightedFolderId, handleFolderClick }) => {
    console.log("Highlighted Folder ID in Map:", highlightedFolderId);
    const [filter, setFilter] = useState('Syndicat');
    const [selectedType, setSelectedType] = useState('ME');
    const [filteredGeoJsonData, setFilteredGeoJsonData] = useState(null);
    const [initialBounds, setInitialBounds] = useState(null);
    const [selectedBounds, setSelectedBounds] = useState(null);
    const [zoomLevel, setZoomLevel] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [SelectedMEId, setSelectedMEId] = useState(null);
    const [SelectedMEName, setSelectedMEName] = useState(null);
    const [highlightedMEId, setHighlightedMEId] = useState(null);
    const mapRef = useRef();
    const geoJsonLayerRefME = useRef();  // Référence pour ME
    const geoJsonLayerRefMO = useRef();  // Référence pour MO
    const geoJsonLayerRefPPG = useRef(); // Référence pour PPG
    const geoJsonLayerRefCEME = useRef(); // Référence pour CE_ME
    const selectedFolderIdRef = useRef(selectedFolderId);
    let maVariable = null;


    useEffect(() => {
        selectedFolderIdRef.current = selectedFolderId; // Mets à jour la référence à chaque changement
    }, [selectedFolderId]);


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


    // Effect to update MO tooltips when selectedFolderId changes
    useEffect(() => {
        if (geoJsonLayerRefMO.current && filteredGeoJsonData?.MO.length > 0) {
            geoJsonLayerRefMO.current.eachLayer(layer => {
                const feature = layer.feature;

                // Supprimer les tooltips existants
                layer.unbindTooltip();

                // Si selectedFolderId est null, afficher ALIAS
                if (!selectedFolderIdRef.current) {
                    layer.bindTooltip(labelMO(feature), {
                        permanent: true,
                        direction: "auto",
                        className: "mo-label"
                    });
                }
            });
        }
    }, [selectedFolderId, filteredGeoJsonData]);

    // Effect to update ME tooltips when selectedFolderId changes
    useEffect(() => {
        if (geoJsonLayerRefME.current && filteredGeoJsonData?.ME.length > 0) {
            geoJsonLayerRefME.current.eachLayer(layer => {
                const feature = layer.feature;

                // Supprimer les tooltips existants
                layer.unbindTooltip();
                // Si selectedFolderId est non null, afficher "bonjour" pour les ME
                if (selectedFolderIdRef.current) {
                    layer.bindTooltip(labelME(feature), {
                        permanent: true,
                        direction: "auto",
                        className: "mo-label"
                    });
                }

            });
        }
    }, [selectedFolderId, filteredGeoJsonData]);

    // labelMO and labelME functions
    const labelMO = (feature) => {
        return feature.properties.ALIAS; // Renvoie l'ALIAS ou un message par défaut
    };

    const labelME = (feature) => {
        return feature.id; // Retourne le texte de l'étiquette pour ME
    };


    const onEachFeatureMO = (feature, layer) => {
        layer.on({
            click: () => {
                if (selectedFolderIdRef.current == null) {
                    const bounds = layer.getBounds();
                    setSelectedBounds(bounds);

                    handleFolderClick({
                        id: feature.id,
                        name: feature.properties.NOM_MO,
                        path: feature.properties.path || '',
                        files: feature.properties.files || []
                    });

                    // Enlève le surlignage après le clic
                    setSelectedFolderId(feature.id);
                    setHighlightedFolderId(null);
                    layer.setStyle(style(feature)); // Réapplique le style normal
                    geoJsonLayerRefMO.current.eachLayer((layer) => {
                        layer.setStyle(style(layer.feature, highlightedFolderId, highlightedMEId, selectedFolderId));
                    });
                    console.log(`selectedFolderIdRef.current: ${selectedFolderIdRef.current}`);
                    console.log(`selectedFolderIdRef.current: ${selectedFolderIdRef}`);
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
                console.log('Clic détecté sur le ME');
                if (selectedFolderIdRef.current) {
                    const bounds = layer.getBounds();
                    setSelectedBounds(bounds);

                    // Mettre à jour l'état pour le ME sélectionné
                    setSelectedMEId(feature.id);
                    setSelectedMEName(feature.properties.NOM_ME);
                }
            },
            mouseover: () => {
                console.log("alloa", selectedFolderIdRef.current)

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



    useEffect(() => {
        if (geoJsonLayerRefME.current) {
            // Réappliquer le style à chaque changement de selectedFolderId pour la couche ME
            geoJsonLayerRefME.current.eachLayer((layer) => {
                layer.setStyle(style(layer.feature, highlightedFolderId, highlightedMEId, selectedFolderIdRef.current));
            });
        }
    }, [selectedFolderId]);



    const style = (feature, highlightedFolderId, highlightedMEId) => {
        const category = feature.properties['type_REF'];
        const isMOSelected = selectedFolderIdRef.current === feature.id;
        const isAnyMOSelected = selectedFolderIdRef.current !== null;
        const featureId = feature.id; // Vérifiez que l'ID est correct


        // Vérifiez si l'entité ME doit être surlignée
        const isMEHighlighted = highlightedMEId === featureId;

        // Vérifiez si l'entité MO doit être surlignée
        const isMOHighlighted = highlightedFolderId === featureId;

        if (isMOHighlighted) {
            return {
                color: 'yellow',
                weight: 5,
                fillOpacity: 0.6,
            };
        }

        if (isMEHighlighted) {
            return {
                color: 'blue', // Couleur pour ME surligné
                weight: 1,
                fillOpacity: 0.6,
            };
        }

        // Styles par défaut pour d'autres types
        if (category === 'MO') {
            if (isAnyMOSelected) {
                return {
                    color: isMOSelected ? 'green' : 'white', // Green pour le MO sélectionné, blanc pour les autres
                    weight: isMOSelected ? 6 : 1, // Weight de 6 pour le MO sélectionné, 2 pour les autres
                    fillColor: 'rgba(0, 255, 0, 0.1)',
                    fillOpacity: 0.1,
                    opacity: 1,
                    interactive: selectedFolderIdRef.current === null
                };
            } else {
                return {
                    color: 'green', // Tous les MO sont verts si aucun n'est sélectionné
                    weight: 5, // Weight de 5 si aucun MO sélectionné
                    fillColor: 'rgba(0, 255, 0, 0.1)',
                    fillOpacity: 0.1,
                    opacity: 1,
                    interactive: true // Interactif si aucun n'est sélectionné
                };
            }
        }
        if (category === 'PPG' || category === 'ME') {
            return {
                color: 'gray',
                weight: 2,
                fillOpacity: 0.3
            };
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

    const showSelectedFolderId = () => {
        if (selectedFolderIdRef.current === null) {
            alert("Current selectedFolderId is null.");
            console.log("Current selectedFolderId is null.");
        } else {
            alert(`Current selectedFolderId: ${selectedFolderIdRef.current}`);
            console.log(`Current selectedFolderId in alert: ${selectedFolderIdRef.current}`);
        }
    };

    // Attendre que les initialBounds soient définis avant de rendre la carte
    if (!initialBounds) {
        return <div>Loading map...</div>;
    }

    return (
        <div className="map-container">
            <div className="sidebar">
                {/* Autres éléments de ton composant ici */}
                <button onClick={showSelectedFolderId}>Afficher selectedFolderId</button>
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
            </div>
            <MapContainer
                bounds={initialBounds}
                className="map"
                whenCreated={map => { mapRef.current = map; }}
            >
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />

                {/* Rendu des polygones par type */}

                {/* Render ME GeoJSON */}
                {filteredGeoJsonData?.ME.length > 0 && (
                    <GeoJSON
                        key={`ME-${filteredGeoJsonData.ME.map(feature => feature.id).join('-')}`} // Utilisation des IDs uniques ici
                        data={filteredGeoJsonData.ME}
                        ref={geoJsonLayerRefME}
                        onEachFeature={(feature, layer) => onEachFeatureME(feature, layer)} // selectedFolderIdRef est déjà accessible dans la fonction
                        style={(feature) => style(feature, highlightedFolderId, highlightedMEId, selectedFolderIdRef.current)} // On passe la référence
                    />
                )}

                {/* Render MO GeoJSON */}
                {filteredGeoJsonData?.MO.length > 0 && (
                    <GeoJSON
                        key={`mo-${filteredGeoJsonData.MO.map(feature => feature.id).join('-')}-${selectedFolderId || 'none'}`} // Utilisation des IDs uniques + selectedFolderId pour forcer le rendu
                        data={filteredGeoJsonData.MO}
                        ref={geoJsonLayerRefMO}
                        onEachFeature={(feature, layer) => onEachFeatureMO(feature, layer)} // selectedFolderIdRef est déjà accessible dans la fonction
                        style={(feature) => style(feature, highlightedFolderId, highlightedMEId, selectedFolderIdRef.current)} // On passe la référence
                    />
                )}


                {/* Render PPG GeoJSON */}
                {filteredGeoJsonData?.PPG.length > 0 && (
                    <GeoJSON
                        key={`ppg-${filteredGeoJsonData.PPG.length}`}
                        data={filteredGeoJsonData.PPG}
                        ref={geoJsonLayerRefPPG}
                        style={(feature) => style(feature, false)}
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
