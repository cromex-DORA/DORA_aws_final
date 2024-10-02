import React from 'react';

const Breadcrumb = ({ department, selectedFolderId, handleBackClick }) => {
    
    return (
        <div className="breadcrumb">
            <span 
                className="breadcrumb-item" 
                onClick={handleBackClick} 
                style={{ cursor: 'pointer', fontWeight: selectedFolderId ? 'normal' : 'bold' }}
            >
                Département {department} {/* Affiche "département" suivi du numéro */}
            </span>
            {selectedFolderId && (
                <>
                    <span className="breadcrumb-separator"> &gt; </span> {/* Séparateur avec le symbole > */}
                    <span className="breadcrumb-item">{selectedFolderId}</span> {/* Nom du folder sélectionné */}
                </>
            )}
        </div>
    );
};

export default Breadcrumb;
