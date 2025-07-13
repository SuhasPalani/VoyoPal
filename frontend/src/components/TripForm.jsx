import React, { useState } from 'react';

const interestsOptions = [
  "Culture & Museums", "Outdoor & Nature", "Food & Drink",
  "Architecture & City Views", "Family-Friendly", "Shopping & Entertainment"
];

const paceOptions = ["relaxed", "fast-paced"];

const transportOptions = ["driving", "public_transit", "walking", "ride_share"];

const budgetOptions = ["budget", "mid-range", "luxury"];

const TripForm = ({ onSubmit, isLoading, initialData = {} }) => {
  const [destination, setDestination] = useState(initialData.destination || 'Chicago');
  const [tripDate, setTripDate] = useState(initialData.tripDate || '');
  const [returnTime, setReturnTime] = useState(initialData.returnTime || '11 PM');
  const [interests, setInterests] = useState(initialData.interests || []);
  const [pace, setPace] = useState(initialData.pace || 'relaxed');
  const [preferredTransport, setPreferredTransport] = useState(initialData.preferredTransport || []);
  const [budgetRange, setBudgetRange] = useState(initialData.budgetRange || 'mid-range');

  const handleInterestChange = (e) => {
    const { value, checked } = e.target;
    setInterests(prev =>
      checked ? [...prev, value] : prev.filter(item => item !== value)
    );
  };

  const handleTransportChange = (e) => {
    const { value, checked } = e.target;
    setPreferredTransport(prev =>
      checked ? [...prev, value] : prev.filter(item => item !== value)
    );
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      destination,
      tripDate,
      returnTime,
      interests,
      pace,
      preferredTransport,
      budgetRange
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <h2>Plan Your Trip</h2>
      <div className="form-group">
        <label htmlFor="destination">Destination:</label>
        <input
          type="text"
          id="destination"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="tripDate">Trip Date:</label>
        <input
          type="date"
          id="tripDate"
          value={tripDate}
          onChange={(e) => setTripDate(e.target.value)}
          required
        />
      </div>
      <div className="form-group">
        <label htmlFor="returnTime">Return Time (e.g., 11 PM):</label>
        <input
          type="text"
          id="returnTime"
          value={returnTime}
          onChange={(e) => setReturnTime(e.target.value)}
          placeholder="e.g., 11 PM"
          required
        />
      </div>

      <div className="form-group">
        <label>Interests:</label>
        <div className="checkbox-group">
          {interestsOptions.map(option => (
            <label key={option}>
              <input
                type="checkbox"
                value={option}
                checked={interests.includes(option)}
                onChange={handleInterestChange}
              />
              {option}
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="pace">Pace:</label>
        <select id="pace" value={pace} onChange={(e) => setPace(e.target.value)}>
          {paceOptions.map(option => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </div>

      <div className="form-group">
        <label>Preferred Transportation:</label>
        <div className="checkbox-group">
          {transportOptions.map(option => (
            <label key={option}>
              <input
                type="checkbox"
                value={option}
                checked={preferredTransport.includes(option)}
                onChange={handleTransportChange}
              />
              {option.replace('_', ' ')}
            </label>
          ))}
        </div>
      </div>

      <div className="form-group">
        <label htmlFor="budgetRange">Budget Range:</label>
        <select id="budgetRange" value={budgetRange} onChange={(e) => setBudgetRange(e.target.value)}>
          {budgetOptions.map(option => (
            <option key={option} value={option}>{option}</option>
          ))}
        </select>
      </div>

      <button type="submit" disabled={isLoading} className="button-primary">
        {isLoading ? 'Generating Suggestions...' : 'Get Suggestions'}
      </button>
    </form>
  );
};

export default TripForm;