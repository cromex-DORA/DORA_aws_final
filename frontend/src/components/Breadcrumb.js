import React from 'react';

const Breadcrumb = ({ department, selectedFolderId, handleBackClick }) => {
    return (
        <div className="breadcrumb">
            <span 
                className="breadcrumb-item" 
                onClick={handleBackClick} 
                style={{ cursor: 'pointer', fontWeight: selectedFolderId ? 'normal' : 'bold' }}
            >
                {department} {/* Affiche le numéro du département */}
            </span>
            {selectedFolderId && (
                <>
                    <span className="breadcrumb-separator"> ➔ </span> {/* Séparateur */}
                    <span className="breadcrumb-item">{selectedFolderId}</span> {/* Nom du folder sélectionné */}
                </>
            )}
        </div>
    );
};

export default Breadcrumb;
