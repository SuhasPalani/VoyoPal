import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { useAuth } from './hooks/useAuth.js'; // Custom hook for authentication context

// Import Pages
import HomePage from './pages/HomePage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import RegisterPage from './pages/RegisterPage.jsx';
import PlanTripPage from './pages/PlanTripPage.jsx';
import SavedTripsPage from './pages/SavedTripsPage.jsx';

// Main App component
function App() {
  const { isAuthenticated, logout } = useAuth();

  return (
    <Router>
      <nav className="navbar">
        <div className="navbar-brand">
          <Link to="/">VoyagePal</Link>
        </div>
        <ul className="navbar-nav">
          {isAuthenticated ? (
            <>
              <li className="nav-item">
                <Link to="/plan-trip">Plan New Trip</Link>
              </li>
              <li className="nav-item">
                <Link to="/saved-trips">My Trips</Link>
              </li>
              <li className="nav-item">
                <button onClick={logout} className="nav-link-button">Logout</button>
              </li>
            </>
          ) : (
            <>
              <li className="nav-item">
                <Link to="/login">Login</Link>
              </li>
              <li className="nav-item">
                <Link to="/register">Register</Link>
              </li>
            </>
          )}
        </ul>
      </nav>

      <div className="container">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          {/* Protected Routes */}
          {isAuthenticated ? (
            <>
              <Route path="/plan-trip" element={<PlanTripPage />} />
              <Route path="/saved-trips" element={<SavedTripsPage />} />
            </>
          ) : (
            // Redirect unauthenticated users trying to access protected routes
            <Route path="*" element={<LoginPage />} />
          )}
        </Routes>
      </div>
    </Router>
  );
}

export default App;