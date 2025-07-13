import React from 'react';

const LoadingSpinner = () => {
  return (
    <div className="spinner-container">
      <div className="spinner"></div>
      <p style={{ color: '#ccc', textAlign: 'center', marginTop: '10px' }}>Loading...</p>
    </div>
  );
};

export default LoadingSpinner;