import React, { useState, useRef, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import LoadingModal from './LoadingModal';
import { fetchMOThunk } from '../features/geojson/geojsonSlice';

const ContenuMO = ({
    folders,
    files,
    currentPath,
    folderName,
    highlightedFolderId,
    setHighlightedFolderId,
    handleFolderClick,
    selectedFolderId,
    setSelectedFolderId
}) => {
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [fileToUpload, setFileToUpload] = useState(null);
    const fileInputRef = useRef(null);
    const [filteredFolders, setFilteredFolders] = useState(folders);
    const dispatch = useDispatch();


    useEffect(() => {
        const result = folders.filter(folder =>
            folder.name.toLowerCase().includes(searchQuery.toLowerCase())
        );
        setFilteredFolders(result);
    }, [folders, selectedFolderId, searchQuery]);

    const handleSearchChange = (e) => {
        setSearchQuery(e.target.value);
    };

    const downloadFile = async (path) => {
        console.log('Attempting to download file from path:', path);

        const token = localStorage.getItem('token');
        try {
            const url = `${process.env.REACT_APP_IP_SERV}/download_file?file_key=${encodeURIComponent(path)}`;
            console.log('Fetching URL:', url);

            const response = await fetch(url, {
                headers: { 'Authorization': token }
            });

            const text = await response.text();
            console.log('Response text:', text);

            try {
                const data = JSON.parse(text);
                if (data.url) {
                    window.location.href = data.url;
                } else {
                    console.error('Download URL not found in the response');
                }
            } catch (jsonError) {
                console.error('Failed to parse JSON:', jsonError);
            }
        } catch (error) {
            console.error('Échec du téléchargement du fichier:', error);
        }
    };

    const createtableauviergeMO = async () => {
        setIsLoading(true);
        setMessage('');
        const formData = new FormData();
        formData.append('id', selectedFolderId);
        formData.append('name', folderName);
        formData.append('path', currentPath);

        const token = localStorage.getItem('token');
        try {
            const response = await fetch(`${process.env.REACT_APP_IP_SERV}/vierge_DORA`, {
                method: 'POST',
                headers: { 'Authorization': token },
                body: formData,
            });

            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            console.log('Tableau vierge DORA créé !');
            setMessage('Le fichier a été créé avec succès !');
        } catch (error) {
            console.error('Échec de la création du fichier:', error);
            setMessage('Erreur lors de la création du fichier.');
        } finally {
            setIsLoading(false);
        }
    };

    const deleteMO = async () => {
        setIsLoading(true);
        setMessage('');


        const formData = new FormData();
        formData.append('id', selectedFolderId);

        const token = localStorage.getItem('token');
        try {
            const response = await fetch(`${process.env.REACT_APP_IP_SERV}/suppression_MO_GEMAPI`, {
                method: 'POST',
                headers: { 'Authorization': token },
                body: formData,
            });


            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
            await dispatch(fetchMOThunk());
            setSelectedFolderId(null);
            setMessage('Le MO a été supprimé avec succès !');

        } catch (error) {
            console.error('Échec de la suppression du MO:', error);
            setMessage('Erreur lors de la suppression du MO.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleFileChange = (e) => {
        setFileToUpload(e.target.files[0]);
        handleFileUpload(e.target.files[0]); // Appel de la fonction d'importation ici
    };

    const handleFileUpload = async (file) => {
        if (!file) {
            console.error('Aucun fichier sélectionné pour l\'importation.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('NOM_MO', folderName);
        formData.append('CODE_MO', selectedFolderId);
        // Ajoutez d'autres informations nécessaires ici

        const token = localStorage.getItem('token');
        try {
            const response = await fetch(`${process.env.REACT_APP_IP_SERV}/verif_tableau_DORA`, {
                method: 'POST',
                headers: { 'Authorization': token },
                body: formData,
            });

            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            console.log('Fichier importé avec succès !');
            // Gérer la réponse ou rafraîchir les données si nécessaire
        } catch (error) {
            console.error('Échec de l\'importation du fichier:', error);
        }
    };

    const openFileExplorer = () => {
        if (fileInputRef.current) {
            fileInputRef.current.click(); // Simule un clic sur l'input de fichier
        }
    };

    return (
        <div>
            {/* Affichage conditionnel de la barre de recherche et des dossiers */}
            {!selectedFolderId && (
                <div>
                    <input
                        type="text"
                        placeholder="Rechercher un dossier..."
                        value={searchQuery}
                        onChange={handleSearchChange}
                        style={{ marginBottom: '10px', display: 'block' }}
                    />

                    {/* Liste des dossiers */}
                    <ul>
                        {filteredFolders.length > 0 ? (
                            filteredFolders.map((folder) => (
                                <li
                                    key={folder.id}
                                    onClick={() => handleFolderClick(folder)}
                                    onMouseOver={() => setHighlightedFolderId(folder.id)}
                                    onMouseOut={() => setHighlightedFolderId(null)}
                                    style={{
                                        cursor: 'pointer',
                                        color: highlightedFolderId === folder.id ? 'red' : 'blue',
                                        fontWeight: highlightedFolderId === folder.id ? 'bold' : 'normal'
                                    }}
                                >
                                    📁 {folder.name}
                                </li>
                            ))
                        ) : (
                            <p>Aucun dossier trouvé</p>
                        )}
                    </ul>
                </div>
            )}

            {/* Si un dossier est sélectionné, afficher les fichiers et les boutons */}
            {selectedFolderId && (
                <div>
                    <hr />
                    {/* Liste des fichiers */}
                    <ul>
                        {files.map((file, index) => (
                            <li key={index}>
                                <span
                                    onClick={() => downloadFile(selectedFolderId ? `${selectedFolderId}/${file}` : file)}
                                    style={{ cursor: 'pointer', color: 'blue' }}
                                >
                                    {file}
                                </span>
                            </li>
                        ))}
                    </ul>

                    <div style={{ marginTop: '20px' }}>
                        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '10px' }}>
                            <button onClick={createtableauviergeMO}>
                                Créer tableau vierge MO
                            </button>
                            <button onClick={openFileExplorer} style={{ marginLeft: '10px' }}>
                                Vérifier un tableau
                            </button>
                            {/* Nouveau bouton pour supprimer le MO */}
                            <button onClick={deleteMO} style={{ marginLeft: '10px', color: 'red' }}>
                                Supprimer le MO
                            </button>


                            {/* Modal de chargement réutilisable */}
                            <LoadingModal
                                isOpen={isLoading}
                                onRequestClose={() => setIsLoading(false)}
                                message="Création du fichier en cours..."
                            />

                            {/* Message de succès ou d'erreur */}
                            {message && <p>{message}</p>}
                        </div>

                        {/* Champ d'importation de fichier invisible */}
                        <input
                            type="file"
                            ref={fileInputRef}
                            style={{ display: 'none' }} // Cache l'input
                            onChange={handleFileChange}
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

export default ContenuMO;
