import React, { useState, useRef, useEffect } from 'react';
import { useDispatch } from 'react-redux';
import LoadingModal from './LoadingModal';
import SuccessModal from './SuccessModal';
import { fetchMOThunk } from '../features/geojson/geojsonSlice';
import './ContenuMO.css';


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
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isSuccessModalOpen, setIsSuccessModalOpen] = useState(false);
    const fileInputRefRempli = useRef(null); // Pour vérifier un tableau
    const fileInputRefFinal = useRef(null);
    const dispatch = useDispatch();



    useEffect(() => {
        const result = folders.filter(folder =>
            folder.name.toLowerCase().includes(searchQuery.toLowerCase())
        );
        setFilteredFolders(result);
    }, [folders, selectedFolderId, searchQuery]);

    useEffect(() => {
        if (selectedFolderId) {
            dispatch(fetchMOThunk()); // Fetch les fichiers à chaque changement de selectedFolderId
        }
    }, [selectedFolderId, dispatch]);

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
            await dispatch(fetchMOThunk()); // Rafraîchir les fichiers après la création
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

    const uploadfichierrempliMO = (e) => {
        setFileToUpload(e.target.files[0]);
        uploadtableaurempliMO(e.target.files[0]); // Appel de la fonction d'importation ici
    };

    const uploadtableaurempliMO = async (file) => {
        if (!file) {
            console.error('Aucun fichier sélectionné pour l\'importation.');
            return;
        }

        setIsLoading(true);
        setMessage('');

        const formData = new FormData();
        formData.append('file', file);
        formData.append('NOM_MO', folderName);
        formData.append('CODE_MO', selectedFolderId);

        const token = localStorage.getItem('token');
        try {
            const response = await fetch(`${process.env.REACT_APP_IP_SERV}/verif_tableau_DORA`, {
                method: 'POST',
                headers: { 'Authorization': token },
                body: formData,
            });

            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            console.log('Fichier importé avec succès !');
            await dispatch(fetchMOThunk());

            setMessage(
                <>
                    <p>Le fichier a été importé avec succès !</p>
                    <p>Joie !</p>
                    <p>Les fichiers suivants ont été créés :</p>
                    <p>Un fichier tableau_rempli avec le fichier original.</p>
                    <p>Un fichier log avec les erreurs du tableau.</p>
                    <p>Un fichier tableau_final avec le fichier qui devra être utilisé
                        pour Osmose et la base de données DORA. En rouge, les
                        cellules qui sont bloquantes et qui entraineront une
                        impossibilité d'importer cette ligne.
                        (Les autres lignes seront quand même importées.). </p>
                    <p>Une fois que vous êtes satisfait(e) de votre tableau,
                        vous pouvez l'importer dans DORA avec le bouton "import BDD DORA".</p>
                    <p>Une fois sur Dora, vous pourrez exporter les actions de ce syndicat
                        sur Osmose2.</p>
                </>
            );
            setIsSuccessModalOpen(true); // Ouvrir la modal de succès
        } catch (error) {
            console.error('Échec de l\'importation du fichier:', error);
            setMessage('Erreur lors de l\'importation du fichier.');
        } finally {
            setIsLoading(false); // Fermer la modal de chargement
        }
    };

    const uploadfichierfinalMO = (e) => {
        setFileToUpload(e.target.files[0]);
        uploadtableaufinalMO(e.target.files[0]); // Appel de la fonction d'importation ici
    };

    const uploadtableaufinalMO = async (file) => {
        if (!file) {
            console.error("Aucun fichier sélectionné pour l'importation.");
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('NOM_MO', folderName);
        formData.append('CODE_MO', selectedFolderId);

        const token = localStorage.getItem('token');
        try {
            const response = await fetch(`${process.env.REACT_APP_IP_SERV}/upload_tableau_final_vers_DORA`, {
                method: 'POST',
                headers: { 'Authorization': token },
                body: formData,
            });

            if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

            console.log('Fichier .xlsx importé avec succès !');
            setMessage('Le fichier .xlsx a été importé avec succès !');
        } catch (error) {
            console.error("Échec de l'importation du fichier .xlsx :", error);
            setMessage("Erreur lors de l'importation du fichier .xlsx.");
        }
    };

    const openfileexplorerrempliMO = () => {
        if (fileInputRefRempli.current) {
            fileInputRefRempli.current.click(); // Simule un clic sur l'input de fichier
        }
    };
    
    // Fonction pour ouvrir le file explorer pour le tableau final
    const openfileexplorerfinalMO = () => {
        if (fileInputRefFinal.current) {
            fileInputRefFinal.current.click(); // Simule un clic sur l'input de fichier
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

    <div style={{ display: 'flex', justifyContent: 'center', marginTop: '10px' }}>
        <button onClick={createtableauviergeMO} className="action-button">
            Créer tableau vierge MO
        </button>

        {/* Bouton pour Vérifier un tableau */}
        <button onClick={openfileexplorerrempliMO} className="action-button">
            Vérifier un tableau
        </button>

        {/* Bouton pour Importer tableau vérifié dans DORA */}
        <button onClick={openfileexplorerfinalMO} className="action-button">
            Importer tableau vérifié <br /> dans DORA
        </button>

        <button onClick={deleteMO} className="delete-button">
            Supprimer le MO
        </button>

        {/* Modal de chargement */}
        <LoadingModal
            isOpen={isLoading}
            onRequestClose={() => setIsLoading(false)}
            message="Création du fichier en cours..."
        />

        {/* Modal de succès */}
        <SuccessModal
            isOpen={isSuccessModalOpen}
            onRequestClose={() => setIsSuccessModalOpen(false)}
            message={message}
        />
    </div>

    {/* Champ d'importation de fichier pour "Vérifier un tableau" */}
    <input
        type="file"
        ref={fileInputRefRempli}
        style={{ display: 'none' }} // Cache l'input
        onChange={uploadfichierrempliMO} // Gestion de fichier pour le tableau rempli
    />

    {/* Champ d'importation de fichier pour "Importer tableau vérifié pour DORA" */}
    <input
        type="file"
        ref={fileInputRefFinal}
        style={{ display: 'none' }} // Cache l'input
        onChange={uploadfichierfinalMO} // Gestion de fichier pour le tableau final
    />
</div>
            )}
        </div>
    );
};

export default ContenuMO;
