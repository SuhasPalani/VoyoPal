// frontend/src/pages/PlanTripPage.jsx
"use client";

import React, { useState, useEffect } from "react";
import TripForm from "../components/TripForm";
import LocationCard from "../components/LocationCard";
import ItineraryDisplay from "../components/ItineraryDisplay";
import LoadingSpinner from "../components/LoadingSpinner";
import api from "../api/api";

export default function PlanTripPage() {
  const [step, setStep] = useState(1); // 1: Form, 2: Suggestions, 3: Detailed Analysis, 4: Itinerary
  const [tripRequestData, setTripRequestData] = useState(null);
  const [suggestions, setSuggestions] = useState(null);
  const [selectedLocations, setSelectedLocations] = useState([]);
  const [detailedAnalysis, setDetailedAnalysis] = useState(null);
  const [optimizedItinerary, setOptimizedItinerary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  // Initialize tripId from localStorage, or null if not found
  const [tripId, setTripId] = useState(() => {
    if (typeof window !== "undefined") {
      // Check if window is defined (i.e., running in browser)
      return localStorage.getItem("currentTripId") || null;
    }
    return null;
  });

  // Effect to save tripId to localStorage whenever it changes
  useEffect(() => {
    if (typeof window !== "undefined") {
      if (tripId) {
        localStorage.setItem("currentTripId", tripId);
      } else {
        localStorage.removeItem("currentTripId");
      }
    }
  }, [tripId]);

  // Function to handle initial trip form submission
  const handleGetSuggestions = async (data) => {
    setLoading(true);
    setError(null);
    setTripRequestData(data); // Save the original request data
    setSelectedLocations([]); // Reset selected locations for new suggestions
    setDetailedAnalysis(null);
    setOptimizedItinerary(null);

    try {
      const response = await api.post("/trip/plan/initial-suggestions", {
        destination: data.destination,
        return_time: data.returnTime,
        trip_date: data.tripDate,
        interests: data.interests,
        pace: data.pace,
        preferred_transport: data.preferredTransport,
        budget_range: data.budgetRange,
      });
      setSuggestions(response.data);
      setTripId(response.data.trip_id); // Store the generated trip ID (this will trigger useEffect to save to localStorage)
      setStep(2); // Move to suggestions display
    } catch (err) {
      console.error(
        "Error getting initial suggestions:",
        err.response?.data || err.message
      );
      setError(
        err.response?.data?.detail || "Failed to get initial suggestions."
      );
    } finally {
      setLoading(false);
    }
  };

  // Function to handle location selection
  const handleLocationSelect = (location) => {
    setSelectedLocations((prev) =>
      prev.some((loc) => loc.name === location.name)
        ? prev.filter((loc) => loc.name !== location.name)
        : [...prev, location]
    );
  };

  // Function to get detailed analysis
  const handleGetDetailedAnalysis = async () => {
    if (selectedLocations.length === 0) {
      setError("Please select at least one location.");
      return;
    }
    // Ensure tripId is available before proceeding
    if (!tripId) {
      setError("Trip ID is missing. Please start a new plan.");
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const response = await api.post("/trip/plan/detailed-analysis", {
        trip_id: tripId, // Use the stored trip ID
        destination: tripRequestData.destination,
        trip_date: tripRequestData.tripDate,
        return_time: tripRequestData.returnTime,
        user_preferences: {
          interests: tripRequestData.interests,
          pace: tripRequestData.pace,
          preferred_transport: tripRequestData.preferredTransport,
          budget_range: tripRequestData.budgetRange,
        },
        selected_locations: selectedLocations,
      });
      setDetailedAnalysis(response.data);
      setStep(3); // Move to detailed analysis display
    } catch (err) {
      console.error(
        "Error getting detailed analysis:",
        err.response?.data || err.message
      );
      setError(
        err.response?.data?.detail || "Failed to get detailed analysis."
      );
    } finally {
      setLoading(false);
    }
  };

  // Function to optimize itinerary
  const handleOptimizeItinerary = async () => {
    // Ensure tripId is available before proceeding
    if (!tripId) {
      setError("Trip ID is missing. Please start a new plan.");
      return;
    }
    setLoading(true);
    setError(null);

    try {
      const response = await api.post("/trip/plan/optimize-itinerary", {
        trip_id: tripId, // Use the stored trip ID
        destination: tripRequestData.destination,
        trip_date: tripRequestData.tripDate,
        return_time: tripRequestData.returnTime,
        user_preferences: {
          interests: tripRequestData.interests,
          pace: tripRequestData.pace,
          preferred_transport: tripRequestData.preferredTransport,
          budget_range: tripRequestData.budgetRange,
        },
        selected_locations: selectedLocations,
      });
      setOptimizedItinerary(response.data);
      setStep(4); // Move to itinerary display
    } catch (err) {
      console.error(
        "Error optimizing itinerary:",
        err.response?.data || err.message
      );
      setError(err.response?.data?.detail || "Failed to optimize itinerary.");
    } finally {
      setLoading(false);
    }
  };

  // Function to reset the planning process
  const startOver = () => {
    setStep(1);
    setTripRequestData(null);
    setSuggestions(null);
    setSelectedLocations([]);
    setDetailedAnalysis(null);
    setOptimizedItinerary(null);
    setTripId(null); // Clear tripId from state
    localStorage.removeItem("currentTripId"); // Clear from localStorage
    setError(null);
  };

  return (
    <div>
      <h1>Plan Your Day Trip</h1>
      {error && <p className="error-message">{error}</p>}
      {loading && <LoadingSpinner />}

      {step === 1 && !loading && (
        <TripForm onSubmit={handleGetSuggestions} isLoading={loading} />
      )}

      {step === 2 && suggestions && !loading && (
        <>
          <h2>AI Suggestions for {tripRequestData.destination}</h2>
          <p>
            <strong>Weather:</strong> {suggestions.general_weather_advice}
          </p>
          <p>
            <strong>Clothing:</strong> {suggestions.clothing_suggestion}
          </p>
          <p>
            <strong>Umbrella Needed:</strong>{" "}
            {suggestions.umbrella_needed ? "Yes" : "No"}
          </p>

          <h3>Select Locations for Your Trip:</h3>
          <div className="suggestions-grid">
            {suggestions.location_suggestions.map((loc, index) => (
              <LocationCard
                key={index}
                location={loc}
                onSelect={handleLocationSelect}
                isSelected={selectedLocations.some(
                  (selected) => selected.name === loc.name
                )}
              />
            ))}
          </div>
          <div className="button-group">
            <button
              onClick={handleGetDetailedAnalysis}
              disabled={selectedLocations.length === 0 || loading}
              className="button-primary"
            >
              {loading
                ? "Analyzing..."
                : `Get Detailed Analysis (${selectedLocations.length} selected)`}
            </button>
            <button onClick={startOver} className="button-secondary">
              Start Over
            </button>
          </div>
        </>
      )}

      {step === 3 && detailedAnalysis && !loading && (
        <>
          <h2>Detailed Trip Analysis</h2>
          <div className="weather-info">
            <h3>Weather Summary</h3>
            <p>{detailedAnalysis.weather_summary}</p>
            <p>
              <strong>Clothing:</strong> {detailedAnalysis.clothing_suggestion}
            </p>
            <p>
              <strong>Umbrella:</strong>{" "}
              {detailedAnalysis.carry_umbrella ? "Yes" : "No"}
            </p>
          </div>
          <div className="travel-tips-info">
            <h3>Money & Transport Tips</h3>
            <p>
              <strong>Money Tips:</strong> {detailedAnalysis.general_money_tips}
            </p>
            <p>
              <strong>Transport Tips:</strong>{" "}
              {detailedAnalysis.transportation_tips}
            </p>
            <p>
              <strong>Other Items:</strong>{" "}
              {detailedAnalysis.other_carry_items.join(", ")}
            </p>
            <p>
              <strong>Est. Gas Cost:</strong>{" "}
              {detailedAnalysis.estimated_gas_cost_usd !== null
                ? `$${detailedAnalysis.estimated_gas_cost_usd.toFixed(2)}`
                : "N/A"}
            </p>
            <p>
              <strong>Est. Public Transit Cost:</strong>{" "}
              {detailedAnalysis.estimated_public_transit_cost_usd !== null
                ? `$${detailedAnalysis.estimated_public_transit_cost_usd.toFixed(
                    2
                  )}`
                : "N/A"}
            </p>
            <p>
              <strong>Est. Ride-Share Cost:</strong>{" "}
              {detailedAnalysis.estimated_ride_share_cost_usd !== null
                ? `$${detailedAnalysis.estimated_ride_share_cost_usd.toFixed(
                    2
                  )}`
                : "N/A"}
            </p>
          </div>
          <div className="button-group">
            <button
              onClick={handleOptimizeItinerary}
              disabled={loading}
              className="button-primary"
            >
              {loading ? "Optimizing..." : "Optimize Itinerary"}
            </button>
            <button onClick={startOver} className="button-secondary">
              Start Over
            </button>
          </div>
        </>
      )}

      {step === 4 && optimizedItinerary && !loading && (
        <>
          <ItineraryDisplay
            itinerary={optimizedItinerary}
            analysis={detailedAnalysis}
          />
          <div className="button-group">
            <button onClick={startOver} className="button-primary">
              Plan Another Trip
            </button>
          </div>
        </>
      )}
    </div>
  );
}
