import React from 'react';

const FiltretypeMO = ({ setSelectedtypeMO }) => {
    return (
        <div className="filter-component" style={{ marginBottom: '10px' }}>
            <h2>Type de MO</h2>
            <select
                onChange={(e) => {
                    console.log("New Selected Option:", e.target.value);
                    setSelectedtypeMO(e.target.value);
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
