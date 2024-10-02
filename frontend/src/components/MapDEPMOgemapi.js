import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
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

const MapDEPMOgemapi = ({ geoJsonData, selectedFolderId, highlightedFolderId, setHighlightedFolderId, handleFolderClick }) => {
    console.log("Highlighted Folder ID in Map:", highlightedFolderId);
    const [filter, setFilter] = useState('Syndicat');
    const [selectedType, setSelectedType] = useState('ME');
    const [filteredGeoJsonData, setFilteredGeoJsonData] = useState(null);
    const [initialBounds, setInitialBounds] = useState(null);
    const [selectedBounds, setSelectedBounds] = useState(null);
    const [zoomLevel, setZoomLevel] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const mapRef = useRef();
    const geoJsonLayerRefME = useRef();  // Référence pour ME
    const geoJsonLayerRefMO = useRef();  // Référence pour MO
    const geoJsonLayerRefPPG = useRef(); // Référence pour PPG
    const geoJsonLayerRefCEME = useRef(); // Référence pour CE_ME

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

    // Effect to update ME tooltips when selectedFolderId changes
    // Effect to update MO tooltips when selectedFolderId changes
    useEffect(() => {
        if (geoJsonLayerRefMO.current && filteredGeoJsonData?.MO.length > 0) {
            geoJsonLayerRefMO.current.eachLayer(layer => {
                const feature = layer.feature;

                // Supprimer les tooltips existants
                layer.unbindTooltip();

                // Si selectedFolderId est null, afficher ALIAS
                if (!selectedFolderId) {
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
                if (selectedFolderId && feature.properties['type_REF'] === 'ME') {
                    layer.bindTooltip(labelME(feature), {
                        permanent: true,
                        direction: "auto",
                        className: "me-label"
                    });
                }
            });
        }
    }, [selectedFolderId, filteredGeoJsonData]);


    // labelMO and labelME functions
    const labelMO = (feature) => {
        return feature.properties.ALIAS || 'Pas d\'alias'; // Renvoie l'ALIAS ou un message par défaut
    };

    const labelME = (feature) => {
        return 'Bonjour'; // Retourne le texte de l'étiquette pour ME
    };

    useEffect(() => {
        if (highlightedFolderId && geoJsonLayerRefMO.current) {
            let entityExists = false; // Flag to check if the entity exists
    
            geoJsonLayerRefMO.current.eachLayer((layer) => {
                const featureId = layer.feature.properties.id; // Assuming 'id' is the common identifier
                
                if (featureId === highlightedFolderId) {
                    entityExists = true; // Entity found
                    layer.setStyle({ color: 'yellow', weight: 5 }); // Highlight style
                } else {
                    layer.setStyle({ color: 'green', weight: 1 }); // Default style
                }
            });
    
            // Log whether the entity was found or not
            console.log(`Entity with ID ${highlightedFolderId} exists: ${entityExists}`);
        }
    }, [highlightedFolderId]); // Re-run when highlightedFolderId changes
    

    const onEachFeature = (feature, layer) => {
        const isMO = feature.properties['type_REF'] === 'MO';
        const isME = feature.properties['type_REF'] === 'ME';
    
        layer.on({
            click: () => {
                // Si selectedFolderId est null, gère les clics sur les MO
                if (isMO && !selectedFolderId) {
                    const bounds = layer.getBounds();
                    console.log("bounds", bounds);
                    setSelectedBounds(bounds);
    
                    // Appeler handleFolderClick avec l'ID du dossier correspondant
                    if (handleFolderClick) {
                        handleFolderClick({
                            id: feature.id,
                            name: feature.properties.NOM_MO,
                            path: feature.properties.path || '',
                            files: feature.properties.files || []
                        });
                    }
                }
                // Si selectedFolderId n'est pas null, gère les clics sur les ME
                else if (isME && selectedFolderId) {
                    console.log(`ME clicked with selectedFolderId: ${selectedFolderId}`);
                    // Ajoute ici le code pour gérer le clic sur ME
                }
            },
            mouseover: () => {
                // Appliquer la surbrillance seulement pour MO
                if (isMO) {
                    setHighlightedFolderId(feature.id);
                    layer.setStyle(style(feature, true)); // Applique le style de surbrillance
                }
            },
            mouseout: () => {
                // Garde le surlignage jusqu'à ce que la souris soit complètement sortie de la zone du feature
                if (highlightedFolderId === feature.id) {
                    layer.setStyle(style(feature, false)); // Réapplique le style normal seulement si l'ID correspond
                }
                setHighlightedFolderId(null);
            }
        });
    };
    
    

    const style = (feature, highlightedFolderId) => {
        const category = feature.properties['type_REF'];
        const featureId = feature.properties.id; // Assuming 'id' is the common identifier
    
        // Check if the current feature should be highlighted
        const isHighlighted = highlightedFolderId === featureId;
    
        if (isHighlighted) {
            return {
                color: 'yellow',
                weight: 5,
                fillOpacity: 0.6
            };
        }
    
        if (category === 'MO') {
            return {
                color: 'green',
                weight: 5,
                fillColor: 'rgba(0, 255, 0, 0.1)',
                fillOpacity: 0.1,
                opacity: 1,
            };
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
    
        return {};
    };

    // Attendre que les initialBounds soient définis avant de rendre la carte
    if (!initialBounds) {
        return <div>Loading map...</div>;
    }

    return (
        <div className="map-container">
            <div className="sidebar">
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
                        key={`me-${filteredGeoJsonData.ME.length}`}
                        data={filteredGeoJsonData.ME}
                        ref={geoJsonLayerRefME}
                        onEachFeature={onEachFeature}
                        style={(feature) => style(feature, false)}
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

                {/* Render MO GeoJSON */}
                {filteredGeoJsonData?.MO.length > 0 && (
                    <GeoJSON
                        key={`mo-${filteredGeoJsonData.MO.length}`}
                        data={filteredGeoJsonData.MO}
                        ref={geoJsonLayerRefMO}
                        onEachFeature={onEachFeature}
                        style={(feature) => style(feature, highlightedFolderId)}
                    />
                )}


                {selectedBounds && <ZoomToBounds bounds={selectedBounds} />}
                <MapEvents setZoomLevel={setZoomLevel} />
            </MapContainer>
        </div>
    );
};

export default MapDEPMOgemapi;
