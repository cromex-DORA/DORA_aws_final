import React, { useEffect, useState } from 'react';

const TableauPAOT = ({ folderName, selectedFolderId, selectedMEId }) => {
    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`${process.env.REACT_APP_IP_SERV}/your_endpoint`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        folderName,
                        selectedFolderId,
                        selectedMEId,
                    }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }

                const result = await response.json();
                setData(result); // Ajustez selon la structure des données reçues
            } catch (error) {
                console.error('Erreur lors de la récupération des données:', error);
                setError(error.message);
            } finally {
                setIsLoading(false);
            }
        };

        fetchData();
    }, [folderName, selectedFolderId, selectedMEId]); // Dépendances pour recharger les données

    if (isLoading) return <div>Chargement...</div>;
    if (error) return <div>Erreur: {error}</div>;

    return (
        <div>
            <h4>Données pour le dossier: {folderName}</h4>
            <table>
                <thead>
                    <tr>
                        {/* Remplacez ces en-têtes par ceux correspondant à vos données */}
                        <th>ID</th>
                        <th>Nom</th>
                        <th>Description</th>
                        {/* Ajoutez d'autres en-têtes si nécessaire */}
                    </tr>
                </thead>
                <tbody>
                    {data.map(item => (
                        <tr key={item.id}>
                            <td>{item.id}</td>
                            <td>{item.name}</td>
                            <td>{item.description}</td>
                            {/* Ajoutez d'autres cellules si nécessaire */}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default TableauPAOT;
