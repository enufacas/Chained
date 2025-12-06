import React from 'react';
import './Header.css';

function Header({ systemStatus }) {
  const homeUrl = window.ENV?.AG_UI_FRONTEND_URL || '#';
  const isHomeConfigured = window.ENV?.AG_UI_FRONTEND_URL;

  return (
    <div className="header">
      <div className="header-left">
        <a 
          href={homeUrl} 
          className="home-btn"
          style={{ 
            opacity: isHomeConfigured ? 1 : 0.5,
            cursor: isHomeConfigured ? 'pointer' : 'not-allowed'
          }}
          onClick={(e) => !isHomeConfigured && e.preventDefault()}
          title={isHomeConfigured ? 'Home' : 'Home URL not configured'}
        >
          🏠 Home
        </a>
        <h1>🤖 AG-ORGANISM - AGENT COORDINATION</h1>
      </div>
      <div className="system-status">STATUS: {systemStatus}</div>
    </div>
  );
}

export default Header;
