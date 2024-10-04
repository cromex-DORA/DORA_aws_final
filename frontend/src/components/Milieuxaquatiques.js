import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import MapDEPMOgemapi from './MapDEPMOgemapi';
import ContenuMO from './ContenuMO';
import Breadcrumb from './Breadcrumb';
import ContenuSousRef from './ContenuSousRef';
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

    const handleMESelect = (meId) => {
        setSelectedMEId(meId);
        console.log('ME sélectionnée ID:', meId); // Vérifiez que l'ID est correctement passé
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
            <div className="other-section">
                {/* Autres sections ou informations */}
            </div>
        </div>
    );
};

export default Milieuxaquatiques;
