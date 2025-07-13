import React, { useEffect, useState } from 'react';
import api from '../api/api.js';
import LoadingSpinner from '../components/LoadingSpinner.jsx';

const SavedTripsPage = () => {
  const [savedTrips, setSavedTrips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchSavedTrips = async () => {
      try {
        const response = await api.get('/trip/trips');
        setSavedTrips(response.data);
      } catch (err) {
        console.error('Error fetching saved trips:', err.response?.data || err.message);
        setError(err.response?.data?.detail || 'Failed to fetch saved trips.');
      } finally {
        setLoading(false);
      }
    };

    fetchSavedTrips();
  }, []);

  if (loading) {
    return <LoadingSpinner />;
  }

  if (error) {
    return <p className="error-message">{error}</p>;
  }

  return (
    <div>
      <h1>My Saved Trips</h1>
      {savedTrips.length === 0 ? (
        <p style={{color: '#ccc', textAlign: 'center'}}>No saved trips yet. Start planning one!</p>
      ) : (
        <div className="card-list">
          {savedTrips.map(trip => (
            <div key={trip.id} className="list-item-card">
              <h3>{trip.destination} - {new Date(trip.trip_date).toLocaleDateString()}</h3>
              <p>Return Time: {trip.return_time}</p>
              <p>Pace: {trip.preferences?.pace || 'N/A'}</p>
              <p>Selected Locations: {trip.selected_locations?.map(loc => loc.name).join(', ') || 'None'}</p>
              {trip.itinerary && trip.itinerary.length > 0 && (
                <p>Itinerary Steps: {trip.itinerary.length}</p>
              )}
              {trip.estimated_costs?.overall_total_estimated_cost_usd && (
                <p>Est. Total Cost: ${trip.estimated_costs.overall_total_estimated_cost_usd.toFixed(2)}</p>
              )}
              {/* You can add a button here to view full details of a saved trip */}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SavedTripsPage;