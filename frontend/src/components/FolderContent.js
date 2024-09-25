import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import MapDEPMOgemapi from './MapDEPMOgemapi';
import FolderList from './FolderList';
import Breadcrumb from './Breadcrumb'; // Import du Breadcrumb
import { jwtDecode } from 'jwt-decode'; // Import correct
import './FolderContent.css';
import { fetchMOThunk, fetchPPGThunk, fetchMEThunk, fetchCEMEThunk } from '../features/geojson/geojsonSlice';

const FolderContent = () => {  // Reçois le département en tant que prop
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
        // Décoder le token pour obtenir le département
        const token = localStorage.getItem('token');
        if (token) {
            const decoded = jwtDecode(token); // Utilisation correcte de jwtDecode
            setDepartment(decoded.CODE_DEP); // Stocke le CODE_DEP dans l'état
        }
    }, []);

    useEffect(() => {
        dispatch(fetchMOThunk());
        dispatch(fetchPPGThunk());
        dispatch(fetchMEThunk());
        dispatch(fetchCEMEThunk());
    }, [dispatch]);

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

    const createFile = async () => {
        const formData = new FormData();
        formData.append('id', selectedFolderId);
        formData.append('name', folderName);
        formData.append('path', currentPath);

        const token = localStorage.getItem('token');
        try {
            const response = await fetch(`${process.env.REACT_APP_IP_SERV}/vierge_DORA`, {
                method: 'POST',
                headers: {
                    'Authorization': token,
                },
                body: formData,
            });

            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            console.log('Tableau vierge DORA créé !');
            dispatch(fetchMOThunk());
        } catch (error) {
            console.error('Échec de la création du fichier:', error);
        }
    };

    useEffect(() => {
        if (selectedFolderId) {
            const selectedFolder = folders.find(folder => folder.id === selectedFolderId);
            if (selectedFolder) {
                setFiles(selectedFolder.files || []);
                setCurrentPath(selectedFolder.path || '');
                setFolderName(selectedFolder.name || '');
                setView('files');
            }
        }
    }, [selectedFolderId, folders]);

    const handleFolderClick = (folder) => {
        setSelectedFolderId(folder.id);
        setFiles(folder.files || []);
        setCurrentPath(folder.path || '');
        setFolderName(folder.name || '');
        setView('files');
    };

    const handleBackClick = () => {
        setSelectedFolderId(null);
        setFiles([]);
        setCurrentPath('');
        setFolderName('');
        setView('folders');
    };

    return (
        <div className="app-container">
            <div className="folder-content-container">
                {/* Ajout de la barre d'adresse */}
                <Breadcrumb
                    department={department} // Passe le département décodé depuis le token
                    selectedFolderId={selectedFolderId}
                    handleBackClick={handleBackClick}
                />

                {view === 'files' && (
                    <>
                        <button onClick={handleBackClick} style={{ marginBottom: '10px' }}>
                            Back
                        </button>
                        <button onClick={createFile} style={{ marginBottom: '10px', marginLeft: '10px' }}>
                            Créer fichier DORA
                        </button>
                    </>
                )}
                <FolderList
                    folders={view === 'folders' ? folders : []}
                    files={view === 'files' ? files : []}
                    currentPath={currentPath}
                    folderName={folderName}
                    handleFolderClick={handleFolderClick}
                    highlightedFolderId={highlightedFolderId}
                    setHighlightedFolderId={setHighlightedFolderId}
                    selectedFolderId={selectedFolderId}
                />
            </div>
            <div className="map-container">
                <MapDEPMOgemapi
                    geoJsonData={geoJsonData}
                    setSelectedFolderId={setSelectedFolderId}
                    highlightedFolderId={highlightedFolderId}
                    setHighlightedFolderId={setHighlightedFolderId}
                    selectedFolderId={selectedFolderId}
                    handleFolderClick={handleFolderClick}
                />
            </div>
            <div className="info-panel-section">
                {/* Autres sections ou informations */}
            </div>
            <div className="other-section">
                {/* Autres sections ou informations */}
            </div>
        </div>
    );
};

export default FolderContent;
