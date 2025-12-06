import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Html } from '@react-three/drei';

function AgentLabel({ text, position }) {
  const htmlRef = useRef();

  // Follow parent position
  useFrame(() => {
    if (htmlRef.current) {
      // Position is automatically updated by parent group
    }
  });

  return (
    <Html
      position={[position[0], position[1] + 4, position[2]]}
      center
      distanceFactor={10}
      style={{
        color: '#00ffff',
        fontSize: '12px',
        fontFamily: "'Segoe UI', sans-serif",
        background: 'rgba(10, 14, 26, 0.8)',
        padding: '4px 8px',
        borderRadius: '4px',
        border: '1px solid #00ffff',
        whiteSpace: 'nowrap',
        pointerEvents: 'none',
        textShadow: '0 0 5px rgba(0, 255, 255, 0.5)',
        userSelect: 'none',
      }}
    >
      {text}
    </Html>
  );
}

export default AgentLabel;
