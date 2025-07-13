import React from 'react';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <div className="home-page">
      <h1>Welcome to VoyagePal!</h1>
      <p>Your AI-powered companion for planning the perfect day trip.</p>
      <p>Let us help you optimize your itinerary, predict weather, manage budget, and much more.</p>
      <div className="button-group">
        <Link to="/plan-trip" className="button-primary">Start Planning Now</Link>
        <Link to="/register" className="button-secondary">Register</Link>
      </div>
    </div>
  );
};

export default HomePage;