import React, { useEffect, useRef, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import FiltretypeMO from './FiltretypeMO';
import FiltretypeSOUSREF from './FiltretypeSOUSREF';
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

    const [filter, setFilter] = useState('Syndicat');
    const [selectedType, setSelectedType] = useState('ME');
    const [filteredGeoJsonData, setFilteredGeoJsonData] = useState(null);
    const [initialBounds, setInitialBounds] = useState(null);
    const [selectedBounds, setSelectedBounds] = useState(null);
    const [zoomLevel, setZoomLevel] = useState(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const mapRef = useRef();
    const geoJsonLayerRef = useRef();


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
                const typeREF = feature.properties['type_REF'];

                // Filtrer par TYPE_MO (filtre actuel)
                const passesFilter = filter ? typeMO === filter : true;

                // On s'assure que les MO du type sélectionné sont affichés
                const isMatchingTypeRef = selectedType ? typeREF === selectedType : true;

                // Affiche les polygones qui correspondent au filtre de TYPE_MO,
                // inclut les PPG/ME si sélectionnés et toujours affiche CE_ME
                return passesFilter || isMatchingTypeRef || typeREF === 'CE_ME';
            })
        };

        setFilteredGeoJsonData(updatedFilteredData);
    }
}, [filter, selectedType, geoJsonData]);


    // Update GeoJSON layer style when highlightedFolderId changes
    useEffect(() => {
        if (geoJsonLayerRef.current && filteredGeoJsonData) {
            geoJsonLayerRef.current.eachLayer(layer => {
                const featureId = layer.feature.id;
                const isHighlighted = highlightedFolderId === featureId;

                layer.setStyle(style(layer.feature, isHighlighted)); // Utilisation de la fonction style
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

            // Ajoutez les tooltips uniquement si le zoom est supérieur à 8 
            // et si selectedFolderId est null
            if (zoomLevel > 8 && feature.properties.ALIAS && selectedFolderId === null) {
                layer.bindTooltip(feature.properties.ALIAS, {
                    permanent: true,
                    direction: "center",
                    className: "polygon-label",
                    interactive: false   // Style des étiquettes
                });
            }
        });
    }
}, [zoomLevel, filteredGeoJsonData, selectedFolderId]);

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
                layer.setStyle(style(feature, true)); // Applique le style de surlignage
            },
            mouseout: () => {
                if (feature.id !== highlightedFolderId) {
                    layer.setStyle(style(feature, false)); // Réapplique le style normal
                }
                setHighlightedFolderId(null);
            }
        });
    };

    // Wait for initialBounds to be set before rendering the map
    if (!initialBounds) {
        return <div>Loading map...</div>;
    }

const style = (feature, isHighlighted) => {
    const category = feature.properties['type_REF'];

    if (isHighlighted) {
        return {
            color: 'yellow', // Couleur pour le surlignage
            weight: 5,
            fillOpacity: 0.6
        };
    }

    // Style pour les MO (vert)
    if (feature.properties['type_REF'] === 'MO') {
        return {
            color: 'green', // Couleur des contours en vert
            weight: 5, // Épaisseur des contours
            fillColor: 'rgba(0, 255, 0, 0.1)', // Vert très transparent pour le remplissage
            fillOpacity: 0.1, // Transparence du remplissage
            opacity: 1, // Opacité du contour
        };
    }

    // Style pour les PPG
    if (feature.properties['type_REF'] === 'PPG') {
        return {
            color: 'gray', // Couleur pour PPG
            weight: 2,
            fillOpacity: 0.3
        };
    }

    // Style pour les ME
    if (feature.properties['type_REF'] === 'ME') {
        return {
            color: 'gray', // Couleur pour ME
            weight: 2,
            fillOpacity: 0.3
        };
    }

    // Style pour CE_ME (bleu)
    if (feature.properties['type_REF'] === 'CE_ME') {
        return {
            color: 'blue', // Couleur des contours en bleu
            weight: 1, // Épaisseur des contours
            fillColor: 'rgba(0, 0, 255, 0.2)', // Bleu plus transparent pour le remplissage
            fillOpacity: 0.4, // Transparence du remplissage
            opacity: 1, // Opacité du contour
        };
    }

    return {};
};


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
                bounds={initialBounds} // Set the initial bounds here
                className="map"
                whenCreated={map => { mapRef.current = map; }}
            >
                <TileLayer
                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                    attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                />

                {/* Rendu des polygones CE_ME (doit être en dernier pour être au-dessus) */}
                {filteredGeoJsonData && (
                    <GeoJSON
                        key={`ceme-${filteredGeoJsonData.features.length}`} // Utilisation d'une clé unique pour MO
                        data={filteredGeoJsonData.features.filter(feature => feature.properties['type_REF'] === 'CE_ME')}
                        style={style}
                        onEachFeature={onEachFeature}
                        ref={geoJsonLayerRef}
                    />
                )}        

                {/* Rendu des polygones PPG */}
                {filteredGeoJsonData && (
                    <GeoJSON
                        key={`ppg-${filteredGeoJsonData.features.length}`} // Utilisation d'une clé unique pour PPG
                        data={filteredGeoJsonData.features.filter(feature => feature.properties['type_REF'] === 'PPG')}
                        style={style}
                        onEachFeature={onEachFeature}
                        ref={geoJsonLayerRef}
                    />
                )}

                {/* Rendu des polygones ME */}
                {filteredGeoJsonData && (
                    <GeoJSON
                        key={`me-${filteredGeoJsonData.features.length}`} // Utilisation d'une clé unique pour ME
                        data={filteredGeoJsonData.features.filter(feature => feature.properties['type_REF'] === 'ME')}
                        style={style}
                        onEachFeature={onEachFeature}
                        ref={geoJsonLayerRef}
                    />
                )}

                {/* Rendu des polygones MO (doit être en dernier pour être au-dessus) */}
                {filteredGeoJsonData && (
                    <GeoJSON
                        key={`mo-${filteredGeoJsonData.features.length}`} // Utilisation d'une clé unique pour MO
                        data={filteredGeoJsonData.features.filter(feature => feature.properties['type_REF'] === 'MO')}
                        style={style}
                        onEachFeature={onEachFeature}
                        ref={geoJsonLayerRef}
                    />
                )}

        

                {selectedBounds && <ZoomToBounds bounds={selectedBounds} />}
                <MapEvents setZoomLevel={setZoomLevel} />
            </MapContainer>

        </div>
    );
};

export default MapDEPMOgemapi;
