import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import FiltretypeMO from './FiltretypeMO';
import TabImportShpModal from './TabImportShpModal';
import 'leaflet/dist/leaflet.css';
import './MapDEPMOgemapi.css';
import { Button } from 'react-bootstrap';
import { useMapEvents } from 'react-leaflet';

const ZoomToBounds = ({ bounds }) => {
    const map = useMap();

    useEffect(() => {
        if (bounds) {
            map.fitBounds(bounds); // Ajuste la vue de la carte pour cadrer les limites
        }
    }, [bounds, map]);

    return null;
};

const MapEvents = ({ setZoomLevel }) => {
    useMapEvents({
        zoomend: (e) => {
            const zoom = e.target.getZoom();
            setZoomLevel(zoom);
            console.log("niveau zoom:", zoom); // Affiche le niveau de zoom dans la console
        }
    });

    return null;
};

const MapDEPMOgemapi = ({ geoJsonData, selectedFolderId, highlightedFolderId, setHighlightedFolderId, handleFolderClick }) => {
    console.log("Essai filtre", geoJsonData); // Ajoute le log ici
    
    const [filter, setFilter] = useState('Syndicat');
    const [filteredGeoJsonData, setFilteredGeoJsonData] = useState(null);
    const [initialBounds, setInitialBounds] = useState(null);
    const [selectedBounds, setSelectedBounds] = useState(null);
    const [zoomLevel, setZoomLevel] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const mapRef = useRef();
    const geoJsonLayerRef = useRef();

    // Ajout de l'état pour les catégories PPG et ME
    const [showPPG, setShowPPG] = useState(true); // Afficher PPG par défaut
    const [showME, setShowME] = useState(true);   // Afficher ME par défaut

    const openModal = () => {
        setIsModalOpen(true);
    };

    const closeModal = () => {
        setIsModalOpen(false);
    };

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
                    [bboxData.miny, bboxData.minx], // [latitude minimale, longitude minimale]
                    [bboxData.maxy, bboxData.maxx]  // [latitude maximale, longitude maximale]
                ];
                setInitialBounds(bounds); // Mettre à jour initialBounds
            } catch (error) {
                console.error('Error fetching bounding box:', error);
            }
        };

        fetchInitialBounds();
    }, []);

    useEffect(() => {
        console.log('Initial bounds:', initialBounds); // Vérifiez que les initialBounds sont définis
    }, [initialBounds]);

    // Effect to filter GeoJSON data when geoJsonData or filter changes
    useEffect(() => {
        
        if (geoJsonData) {
            const updatedFilteredData = {
                ...geoJsonData,
                features: geoJsonData.features.filter(feature => {
                    const typeMO = feature.properties['TYPE_MO'];

                    // Filtrer par TYPE_MO (filtre actuel)
                    const passesFilter = filter ? typeMO === filter : true;

                    // Filtrer par PPG et ME en fonction des cases à cocher
                    const isPPG = feature.properties['CATEGORY'] === 'PPG' && showPPG;
                    const isME = feature.properties['CATEGORY'] === 'ME' && showME;

                    // Affiche les polygones qui correspondent au filtre ou à PPG/ME cochés
                    return passesFilter || isPPG || isME;
                })
            };

            setFilteredGeoJsonData(updatedFilteredData);
        }
    }, [filter, geoJsonData, showPPG, showME]);

    // Update GeoJSON layer style when highlightedFolderId changes
    useEffect(() => {
        if (geoJsonLayerRef.current && filteredGeoJsonData) {
            geoJsonLayerRef.current.eachLayer(layer => {
                const featureId = layer.feature.id;
                if (highlightedFolderId === featureId) {
                    layer.setStyle({
                        weight: 8,
                        color: '#ff0000',
                        opacity: 0.8
                    });
                } else {
                    layer.setStyle({
                        weight: 5,
                        color: '#0000ff',
                        opacity: 0.65
                    });
                }
            });
        }
    }, [highlightedFolderId, filteredGeoJsonData]);

    // Effect to update bounds when selectedFolderId changes
    useEffect(() => {
        if (geoJsonLayerRef.current && filteredGeoJsonData && selectedFolderId) {
            geoJsonLayerRef.current.eachLayer(layer => {
                const featureId = layer.feature.id;
                if (featureId === selectedFolderId) {
                    const bounds = layer.getBounds(); // Get the bounds of the selected feature
                    setSelectedBounds(bounds); // Set the bounds to zoom to
                }
            });
        }
    }, [selectedFolderId, filteredGeoJsonData]);


    useEffect(() => {
        if (geoJsonLayerRef.current && filteredGeoJsonData) {
            geoJsonLayerRef.current.eachLayer(layer => {
                const feature = layer.feature;

                // Supprimez les tooltips existants
                layer.unbindTooltip();

                // Ajoutez les tooltips uniquement si le zoom est supérieur à 9
                if (zoomLevel > 8 && feature.properties.ALIAS) {
                    layer.bindTooltip(feature.properties.ALIAS, {
                        permanent: true,
                        direction: "center",
                        className: "polygon-label" // Style des étiquettes
                    });
                }
            });
        }
    }, [zoomLevel, filteredGeoJsonData]);

    const onEachFeature = (feature, layer) => {
        layer.on({
            click: () => {
                const bounds = layer.getBounds();
                console.log("bounds", bounds);
                setSelectedBounds(bounds);

                // Appeler handleFolderClick avec l'ID du dossier correspondant
                if (handleFolderClick) {
                    handleFolderClick({
                        id: feature.id,
                        name: feature.properties.NOM_MO,  // Assurez-vous que le nom du dossier est dans properties
                        path: feature.properties.path || '', // Assurez-vous que le chemin est aussi dans properties
                        files: feature.properties.files || [] // Assurez-vous que les fichiers sont dans properties
                    });
                }
            },
            mouseover: () => {
                setHighlightedFolderId(feature.id);
                layer.setStyle({
                    weight: 8,
                    color: '#ff0000',
                    opacity: 0.8
                });
            },
            mouseout: () => {
                if (feature.id !== highlightedFolderId) {
                    layer.setStyle({
                        weight: 5,
                        color: '#0000ff',
                        opacity: 0.65
                    });
                }
                setHighlightedFolderId(null);
            }
        });
    };

    // Wait for initialBounds to be set before rendering the map
    if (!initialBounds) {
        return <div>Loading map...</div>;
    }

    return (
        <div className="map-container">
            <div className="sidebar">
                <FiltretypeMO selectedOption={filter} setSelectedOption={setFilter} />

                {/* Légende avec cases à cocher pour PPG et ME */}
                <div className="legend">
                    <label>
                        <input
                            type="checkbox"
                            checked={showPPG}
                            onChange={(e) => setShowPPG(e.target.checked)}
                        />
                        Afficher PPG
                    </label>
                    <label>
                        <input
                            type="checkbox"
                            checked={showME}
                            onChange={(e) => setShowME(e.target.checked)}
                        />
                        Afficher ME
                    </label>
                </div>

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
                bounds={initialBounds} // Set the initial bounds here
                className="map"
                whenCreated={map => { mapRef.current = map; }}
            >
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />
                {filteredGeoJsonData && (
                    <GeoJSON
                        key={JSON.stringify(filteredGeoJsonData)}
                        data={filteredGeoJsonData}
                        onEachFeature={onEachFeature}
                        ref={geoJsonLayerRef}
                        style={{
                            weight: 5,
                            color: '#0000ff',
                            opacity: 0.65
                        }}
                    />
                )}
                {selectedBounds && <ZoomToBounds bounds={selectedBounds} />}
                <MapEvents setZoomLevel={setZoomLevel} />
            </MapContainer>
        </div>
    );
};

export default MapDEPMOgemapi;
