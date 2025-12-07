import React from 'react';
import './LoadingScreen.css';

function LoadingScreen() {
  return (
    <div className="loading-screen">
      <div className="loading-spinner"></div>
      <div className="loading-text">INITIALIZING AG-ORGANISM...</div>
    </div>
  );
}

export default LoadingScreen;
