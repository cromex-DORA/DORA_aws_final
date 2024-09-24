// FiltretypeSOUSREF.js
import React from 'react';

const FiltretypeSOUSREF = ({ selectedOption, setSelectedOption }) => {
    return (
        <div className="filter-dropdown">
            <label htmlFor="data-type">Afficher :</label>
            <select
                id="data-type"
                value={selectedOption}
                onChange={(e) => setSelectedOption(e.target.value)}
            >
                <option value="ME">ME</option>
                <option value="PPG">PPG</option>
            </select>
        </div>
    );
};

export default FiltretypeSOUSREF;
