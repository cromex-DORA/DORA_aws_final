import React, { useState, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import MapDEPMOgemapi from './MapDEPMOgemapi';
import ContenuMO from './ContenuMO';
import Breadcrumb from './Breadcrumb';
import ContenuSousRef from './ContenuSousRef';
import TableauPAOT from './TableauPAOT';
import { jwtDecode } from 'jwt-decode';
import './Milieuxaquatiques.css';
import { fetchMOThunk, fetchPPGThunk, fetchMEThunk, fetchCEMEThunk } from '../features/geojson/geojsonSlice';

const Milieuxaquatiques = () => {
    const dispatch = useDispatch();
    const geoJsonMO = useSelector((state) => state.geojson.mo);
    const geoJsonME = useSelector((state) => state.geojson.me);
    const geoJsonPPG = useSelector((state) => state.geojson.ppg);
    const geoJsonCEME = useSelector((state) => state.geojson.ceme);
    const [department, setDepartment] = useState('');
    const [folders, setFolders] = useState([]);
    const [files, setFiles] = useState([]);
    const [currentPath, setCurrentPath] = useState('');
    const [folderName, setFolderName] = useState('');
    const [selectedFolderId, setSelectedFolderId] = useState(null);
    const [view, setView] = useState('folders');
    const [highlightedFolderId, setHighlightedFolderId] = useState(null);
    const [selectedMEId, setSelectedMEId] = useState(null);
    const selectedFolderIdRef = useRef(null);

    const geoJsonData = {
        type: "FeatureCollection",
        features: [
            ...(geoJsonMO?.features || []),
            ...(geoJsonME?.features || []),
            ...(geoJsonPPG?.features || []),
            ...(geoJsonCEME?.features || [])
        ]
    };

    useEffect(() => {
        const token = localStorage.getItem('token');
        if (token) {
            const decoded = jwtDecode(token);
            setDepartment(decoded.CODE_DEP);
        }
    }, []);

    useEffect(() => {
        dispatch(fetchMOThunk());
        dispatch(fetchPPGThunk());
        dispatch(fetchMEThunk());
        dispatch(fetchCEMEThunk());
    }, [dispatch]);

    // Charger les dossiers à partir de geoJsonMO
    useEffect(() => {
        if (geoJsonMO) {
            const folderData = geoJsonMO.features.map(feature => ({
                id: feature.id,
                name: feature.properties.NOM_MO,
                files: feature.properties.files || []
            })) || [];
            setFolders(folderData);
        }
    }, [geoJsonMO]);

    // UseEffect pour réagir aux changements de selectedFolderId
    useEffect(() => {
        if (selectedFolderId === null) {
            // Si selectedFolderId est null, réinitialiser les états dépendants
            setFiles([]);
            setCurrentPath('');
            setFolderName('');
            setView('folders'); // Revenir à la vue des dossiers
        } else {
            // Si selectedFolderId change, trouver le dossier correspondant et mettre à jour les états
            const selectedFolder = folders.find(folder => folder.id === selectedFolderId);
            if (selectedFolder) {
                setFiles(selectedFolder.files || []);
                setCurrentPath(selectedFolder.path || '');
                setFolderName(selectedFolder.name || '');
                setView('files'); // Afficher les fichiers du dossier
            }
        }
    }, [selectedFolderId, folders]);

    const handleFolderClick = (folder) => {
        setSelectedFolderId(folder.id);
        selectedFolderIdRef.current = folder.id;
        setHighlightedFolderId(null);
        // Les états dépendants seront mis à jour via useEffect
    };

    const handleBackClick = () => {
        setSelectedFolderId(null);
        selectedFolderIdRef.current = null;
    };

    const handleMESelect = (meId) => {
        setSelectedMEId(meId);
        console.log('ME sélectionnée ID:', meId); // Vérifiez que l'ID est correctement passé
    };

    const resetSelectedFolderId = () => {
        setSelectedFolderId(null);
        selectedFolderIdRef.current = null; // Réinitialiser également la référence
    };

    return (
        <div className="app-container">
            <div className="folder-content-container">
                <Breadcrumb
                    department={department}
                    selectedFolderId={selectedFolderId}
                    handleBackClick={handleBackClick}
                />

                <ContenuMO
                    folders={view === 'folders' ? folders : []}
                    files={view === 'files' ? files : []}
                    currentPath={currentPath}
                    folderName={folderName}
                    handleFolderClick={handleFolderClick}
                    highlightedFolderId={highlightedFolderId}
                    setHighlightedFolderId={setHighlightedFolderId}
                    selectedFolderId={selectedFolderId}
                    resetSelectedFolderId={resetSelectedFolderId}
                    setSelectedFolderId={setSelectedFolderId}
                />
            </div>
            <div className="map-container">
                <MapDEPMOgemapi
                    geoJsonData={geoJsonData}
                    selectedFolderId={selectedFolderId}
                    setSelectedFolderId={setSelectedFolderId}
                    highlightedFolderId={highlightedFolderId}
                    setHighlightedFolderId={setHighlightedFolderId}
                    handleFolderClick={handleFolderClick}
                    handleMESelect={handleMESelect}
                />
            </div>
            <div className="contenu-sous-ref">
                <ContenuSousRef selectedMEId={selectedMEId} />
            </div>
            <div className="tableau_action_PAOT">
                <h4>Folder ID sélectionné: {selectedFolderId !== null ? selectedFolderId : 'Aucun'}</h4>
                <button onClick={resetSelectedFolderId}>
                    Réinitialiser le dossier sélectionné
                </button>
                <TableauPAOT 
                folderName={folderName} 
                selectedFolderId={selectedFolderId} 
                selectedMEId={selectedMEId} 
            />
            </div>
        </div>
    );
};

export default Milieuxaquatiques;
