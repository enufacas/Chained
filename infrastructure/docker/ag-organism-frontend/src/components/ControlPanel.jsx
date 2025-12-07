import React from 'react';
import './ControlPanel.css';

function ControlPanel({ enableBloom, showConnections, onToggleBloom, onToggleConnections }) {
  const handleResetCamera = () => {
    // This will be handled via a ref or event system if needed
    window.dispatchEvent(new CustomEvent('reset-camera'));
  };

  return (
    <div className="control-panel">
      <button className="control-btn active" onClick={handleResetCamera}>
        Reset View
      </button>
      <button 
        className={`control-btn ${enableBloom ? 'active' : ''}`}
        onClick={onToggleBloom}
      >
        Bloom: {enableBloom ? 'ON' : 'OFF'}
      </button>
      <button 
        className={`control-btn ${showConnections ? 'active' : ''}`}
        onClick={onToggleConnections}
      >
        Connections: {showConnections ? 'ON' : 'OFF'}
      </button>
    </div>
  );
}

export default ControlPanel;
