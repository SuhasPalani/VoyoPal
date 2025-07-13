import React from 'react';

const LocationCard = ({ location, onSelect, isSelected }) => {
  return (
    <div className="suggestion-card">
      <div>
        <h3>{location.name} ({location.type})</h3>
        <p><strong>Description:</strong> {location.description}</p>
        <p><strong>Est. Visit:</strong> {location.estimated_time_spent_minutes} mins</p>
        <p><strong>Admission:</strong> {location.admission_cost_usd === 0 ? 'Free' : (location.admission_cost_usd ? `$${location.admission_cost_usd.toFixed(2)}` : 'Varies/Unknown')}</p>
        <p><strong>Hours:</strong> {location.operating_hours_summary}</p>
        <p><strong>Reasons:</strong> {location.reasons_for_suggestion?.join(', ') || 'N/A'}</p>
      </div>
      <div className="checkbox-wrapper">
        <input
          type="checkbox"
          id={`location-${location.name.replace(/\s/g, '-')}`}
          checked={isSelected}
          onChange={() => onSelect(location)}
        />
        <label htmlFor={`location-${location.name.replace(/\s/g, '-')}`}>Select for Trip</label>
      </div>
    </div>
  );
};

export default LocationCard;