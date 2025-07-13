import React from 'react';

const ItineraryDisplay = ({ itinerary, analysis }) => {
  if (!itinerary || !itinerary.itinerary_steps || !analysis) {
    return null;
  }

  const formatCurrency = (amount) => {
    return amount ? `$${amount.toFixed(2)}` : 'N/A';
  };

  return (
    <div className="itinerary-details">
      <div className="itinerary-summary">
        <h2>Trip Summary</h2>
        <p><strong>Feasibility:</strong> <span className={`status-${itinerary.feasibility_status.replace(/_/g, '-')}`}>{itinerary.feasibility_status.replace(/_/g, ' ').toUpperCase()}</span></p>
        {itinerary.feasibility_notes && <p><strong>Notes:</strong> {itinerary.feasibility_notes}</p>}
        <p><strong>Total Activity Time:</strong> {Math.floor(itinerary.total_activity_time_minutes / 60)}h {itinerary.total_activity_time_minutes % 60}m</p>
        <p><strong>Total Travel Time:</strong> {Math.floor(itinerary.total_travel_time_minutes / 60)}h {itinerary.total_travel_time_minutes % 60}m</p>
        <p><strong>Estimated Itinerary Cost (Admissions):</strong> {formatCurrency(itinerary.total_estimated_cost_usd)}</p>
        <p><strong>Estimated Food & Local Transport:</strong> (See Detailed Analysis)</p>
      </div>

      <h2 style={{marginTop: '2rem'}}>Detailed Itinerary</h2>
      {itinerary.itinerary_steps.map((step, index) => (
        <div key={index} className="itinerary-step">
          <h4>{step.activity}</h4>
          <p className="time">{step.start_time} - {step.end_time}</p>
          <p><strong>Location:</strong> {step.location_name} {step.address && `(${step.address})`}</p>
          {step.transport_mode_to_next && (
            <p><strong>Next Transport:</strong> {step.transport_mode_to_next.replace('_', ' ')} (Est. {step.estimated_travel_time_minutes} mins)</p>
          )}
          {step.notes && <p className="notes">{step.notes}</p>}
        </div>
      ))}

      <div className="weather-info">
        <h3>Weather Information</h3>
        <p>{analysis.weather_summary}</p>
        <p><strong>Clothing:</strong> {analysis.clothing_suggestion}</p>
        <p><strong>Umbrella Needed:</strong> {analysis.carry_umbrella ? 'Yes' : 'No'}</p>
      </div>

      <div className="travel-tips-info">
        <h3>Travel Tips</h3>
        <p><strong>Money Tips:</strong> {analysis.general_money_tips}</p>
        <p><strong>Transportation Tips:</strong> {analysis.transportation_tips}</p>
        <p><strong>Other Items to Carry:</strong></p>
        <ul>
          {analysis.other_carry_items.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      </div>

      <div className="travel-tips-info">
        <h3>Estimated Costs (Detailed)</h3>
        {analysis.estimated_gas_cost_usd !== null && <p><strong>Estimated Gas Cost:</strong> {formatCurrency(analysis.estimated_gas_cost_usd)}</p>}
        {analysis.estimated_public_transit_cost_usd !== null && <p><strong>Estimated Public Transit Cost:</strong> {formatCurrency(analysis.estimated_public_transit_cost_usd)}</p>}
        {analysis.estimated_ride_share_cost_usd !== null && <p><strong>Estimated Ride-Share Cost:</strong> {formatCurrency(analysis.estimated_ride_share_cost_usd)}</p>}
        {analysis.location_info && analysis.location_info.length > 0 && (
          <div>
            <h4>Location Specific Info:</h4>
            {analysis.location_info.map((info, index) => (
              <div key={index}>
                <p><strong>{info.name}:</strong> {info.typical_hours} - {info.quick_fact}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ItineraryDisplay;