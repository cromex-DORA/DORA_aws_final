import React from 'react';

const FiltretypeMO = ({ setSelectedOption }) => {
    return (
        <div className="filter-component" style={{ marginBottom: '10px' }}>
            <h2>Type de MO</h2>
            {/* Liste déroulante */}
            <select
                onChange={(e) => {
                    console.log("New Selected Option:", e.target.value); // <-- Ajoutez ce log ici
                    setSelectedOption(e.target.value);
                }}
                style={{ marginBottom: '10px' }}
            >
                <option value="Syndicat">Syndicat</option>            
                <option value="EPTB">EPTB</option>
                <option value="EPCI">EPCI</option>
            </select>
        </div>
    );
};

export default FiltretypeMO;
