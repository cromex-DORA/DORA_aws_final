import React, { useState } from 'react';

const FolderList = ({
    folders, 
    files, 
    currentPath, 
    folderName, 
    highlightedFolderId, 
    setHighlightedFolderId, 
    handleFolderClick,
    selectedFolderId
}) => {
    const [searchQuery, setSearchQuery] = useState('');

    const handleSearchChange = (e) => {
        setSearchQuery(e.target.value.toLowerCase());
    };

    const filteredFolders = folders.filter(folder =>
        folder.name.toLowerCase().includes(searchQuery)
    );

const downloadFile = async (path) => {
    // Log avant l'appel de fetch pour vérifier que la fonction est bien appelée
    console.log('Attempting to download file from path:', path);

    const token = localStorage.getItem('token');

    try {
        const url = `${process.env.REACT_APP_IP_SERV}/download_file?file_key=${encodeURIComponent(path)}`;
        console.log('Fetching URL du prout:', url);  // Log de l'URL que vous essayez de joindre

        const response = await fetch(url, {
            headers: { 'Authorization': token }
        });

        // Afficher le texte brut de la réponse
        const text = await response.text();
        console.log('Response text du prout:', text);

        // Convertir en JSON si possible
        try {
            const data = JSON.parse(text);
            if (data.url) {
                window.location.href = data.url;  // Redirige vers l'URL de téléchargement
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

    return (
        <div>
            {/* Champ de recherche */}
            <input
                type="text"
                placeholder="Rechercher un dossier..."
                value={searchQuery}
                onChange={handleSearchChange}
                style={{ marginBottom: '10px', display: 'block' }}
            />

            {/* Liste des dossiers filtrés */}
            <ul>
                {filteredFolders.map((folder) => (
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
                ))}
                {files.map((file, index) => (
                    <li key={index}>
                        <span onClick={() => downloadFile(selectedFolderId ? `${selectedFolderId}/${file}` : file)} style={{ cursor: 'pointer', color: 'blue' }}>
                            {file}
                        </span>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default FolderList;
