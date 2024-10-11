import React, { useState, useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';
import { MapContainer, TileLayer, GeoJSON, useMap } from 'react-leaflet';
import { Form, Button, Alert, Row, Col } from 'react-bootstrap';
import { useDispatch } from 'react-redux';
import LoadingModal from './LoadingModal';
import { fetchMOThunk } from '../features/geojson/geojsonSlice';
import 'leaflet/dist/leaflet.css';
import './MO_gemapiTab.css'; // Assurez-vous que ce fichier contient les styles nécessaires


const FitBounds = ({ bounds }) => {
    const map = useMap();

    useEffect(() => {
        if (bounds) {
            map.fitBounds(bounds);
        }
    }, [bounds, map]);

    return null;
};

const MO_gemapiTab = ({ initialBounds }) => {
    const [isLoading, setIsLoading] = useState(false);
    const [files, setFiles] = useState([]);
    const [nomMo, setNomMo] = useState('');
    const [alias, setAlias] = useState('');
    const [codeSiren, setCodeSiren] = useState('');
    const [uploadStatus, setUploadStatus] = useState(null);
    const [geoJsonData, setGeoJsonData] = useState(null);
    const [selectedFeature, setSelectedFeature] = useState(null);
    const dispatch = useDispatch();

    const token = localStorage.getItem('token');

    const onDrop = useCallback((acceptedFiles) => {
        setFiles(acceptedFiles);
    }, []);

    const { getRootProps, getInputProps } = useDropzone({
        onDrop,
        multiple: true,
        accept: {
            'application/octet-stream': ['.shp', '.dbf', '.shx', '.prj','.gpkg']
        }
    });

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!files.length) {
            setUploadStatus('error');
            return;
        }

        const formData = new FormData();
        formData.append('NOM-MO', nomMo);
        files.forEach((file) => {
            formData.append('files', file);
        });

        // Ouvrir le modal de chargement avant le début de l'import
        setIsLoading(true);

        try {
            const response = await fetch(`${process.env.REACT_APP_IP_SERV}/upload_MO_gemapi`, {
                method: 'POST',
                headers: {
                    'Authorization': token
                },
                body: formData
            });

            if (!response.ok) {
                throw new Error('Failed to upload');
            }

            const geoJsonResponse = await response.json();
            setGeoJsonData(geoJsonResponse);
            setUploadStatus('success');

        } catch (error) {
            console.error('Error during upload:', error);
            setUploadStatus('error');
        } finally {
            // Fermer le modal une fois l'import terminé (succès ou échec)
            setIsLoading(false);
        }
    };

    const handleFeatureClick = (feature) => {
        setSelectedFeature(feature);
    };

    const handleSendInfo = async () => {
        if (!selectedFeature) {
            alert('Veuillez sélectionner un polygone.');
            return;
        }
    
        const geometry = selectedFeature.geometry;
        const formData = new FormData();
        formData.append('geometry', JSON.stringify(geometry));
        formData.append('NOM-MO', nomMo);
        formData.append('ALIAS', alias);
        formData.append('CODE_SIRET', codeSiren);
    
        // Ouvrir le modal de chargement avant le début de l'envoi
        setIsLoading(true);
    
        try {
            const response = await fetch(`${process.env.REACT_APP_IP_SERV}/upload_complete_MO_gemapi`, {
                method: 'POST',
                headers: {
                    'Authorization': token
                },
                body: formData
            });
    
            if (!response.ok) {
                throw new Error('Failed to send information');
            }
    
            await dispatch(fetchMOThunk());

            alert('Envoi terminé avec succès !'); // Afficher un message de succès
    
        } catch (error) {
            console.error('Error sending information:', error);
            alert('Erreur lors de l\'envoi des informations.');
        } finally {
            // Fermer le modal une fois l'envoi terminé (succès ou échec)
            setIsLoading(false);
        }
    };


    return (
        <>
            {/* Modal de chargement */}
            <LoadingModal isOpen={isLoading} onRequestClose={() => setIsLoading(false)} message="Chargement en cours..." />

            <Row>
                {/* Colonne de gauche pour la dropzone et le bouton */}
                <Col md={4}>
                    <div className="dropzone-container">
                        <div {...getRootProps({ className: 'dropzone' })}>
                            <input {...getInputProps()} />
                            <p>Glissez-déposez des fichiers ici, ou cliquez pour sélectionner des fichiers (formats .shp, .dbf, .shx, .prj)</p>
                        </div>
                        <Button className="upload-button mt-2" variant="primary" onClick={handleSubmit}>
                            Envoyer
                        </Button>
                    </div>
                </Col>

                {/* Colonne de droite pour la carte et le formulaire */}
                <Col md={8}>
                    <Row>
                        {/* Carte */}
                        <Col md={12}>
                            {uploadStatus === 'success' && geoJsonData && (
                                <div className="map-container">
                                    <Alert variant="success">
                                        Quel polygone ?
                                    </Alert>
                                    <MapContainer
                                        style={{ height: '400px', width: '100%' }}
                                        center={initialBounds?.[0] || [44.837789, -0.57918]} // Assure que les coordonnées sont correctes
                                        zoom={12} // Si tu ne veux pas de valeur par défaut, enlève cette ligne
                                    >
                                        <TileLayer
                                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                                            attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
                                        />
                                        <GeoJSON
                                            data={geoJsonData}
                                            onEachFeature={(feature, layer) => {
                                                layer.on({
                                                    click: () => handleFeatureClick(feature)
                                                });
                                            }}
                                            style={(feature) => ({
                                                color: feature === selectedFeature ? 'blue' : 'gray',  // Surbrillance du polygone sélectionné
                                            })}
                                        />
                                        <FitBounds bounds={initialBounds} />
                                    </MapContainer>
                                </div>
                            )}
                        </Col>
                    </Row>

                    <Row className="mt-3">
                        {/* Formulaire */}
                        <Col md={12}>
                            <div className="form-container">
                                <Form>
                                    <Form.Group controlId="formNomMo">
                                        <Form.Label>NOM-MO</Form.Label>
                                        <Form.Control
                                            type="text"
                                            placeholder="Entrez le NOM-MO"
                                            value={nomMo}
                                            onChange={(e) => setNomMo(e.target.value)}
                                        />
                                    </Form.Group>

                                    <Form.Group controlId="formAlias">
                                        <Form.Label>ALIAS</Form.Label>
                                        <Form.Control
                                            type="text"
                                            placeholder="Entrez l'ALIAS"
                                            value={alias}
                                            onChange={(e) => setAlias(e.target.value)}
                                        />
                                    </Form.Group>

                                    <Form.Group controlId="formCodeSiren">
                                        <Form.Label>CODE_SIREN</Form.Label>
                                        <Form.Control
                                            type="text"
                                            placeholder="Entrez le CODE_SIREN"
                                            value={codeSiren}
                                            onChange={(e) => setCodeSiren(e.target.value)}
                                        />
                                    </Form.Group>
                                </Form>

                                {selectedFeature && (
                                    <Button className="mt-3" variant="success" style={{ position: 'absolute', bottom: '20px', right: '20px' }} onClick={handleSendInfo}>
                                        Envoyer les informations du polygone
                                    </Button>
                                )}
                            </div>
                        </Col>
                    </Row>
                </Col>
            </Row>
        </>
    );
};

export default MO_gemapiTab;
