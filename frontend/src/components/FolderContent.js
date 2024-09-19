import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import MapDEPMOgemapi from './MapDEPMOgemapi';
import FolderList from './FolderList';
import './FolderContent.css';
import { fetchMOThunk } from '../features/geojson/geojsonSlice';

const FolderContent = () => {
    const dispatch = useDispatch();
    const geoJsonData = useSelector((state) => state.geojson.mo); // Utilise le state de Redux pour GeoJSON
    const [folders, setFolders] = useState([]);
    const [files, setFiles] = useState([]);
    const [currentPath, setCurrentPath] = useState('');
    const [folderName, setFolderName] = useState('');
    const [selectedFolderId, setSelectedFolderId] = useState(null);
    const [view, setView] = useState('folders'); // 'folders' or 'files'
    const [highlightedFolderId, setHighlightedFolderId] = useState(null);

    // Appelle fetchContent au chargement du composant
    useEffect(() => {
        dispatch(fetchMOThunk());
    }, [dispatch]);

    // Met à jour les dossiers lorsque geoJsonData change
    useEffect(() => {
        if (geoJsonData) {
            const folderData = geoJsonData.features.map(feature => ({
                id: feature.id,
                name: feature.properties.NOM_MO,
                files: feature.properties.files || []  // Assume files are in properties
            })) || [];
            setFolders(folderData);
        }
    }, [geoJsonData]); // Dépendance sur geoJsonData

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

            console.log('Tableau vierge DORA créé !'); // Log de débogage
            dispatch(fetchMOThunk()); // Actualiser le contenu du dossier après création
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
