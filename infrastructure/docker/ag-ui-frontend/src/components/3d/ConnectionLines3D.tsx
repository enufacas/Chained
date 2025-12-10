/**
 * ConnectionLines3D Component
 * 
 * Renders connection lines between selected agents in 3D space
 */

import * as THREE from 'three';
import { useMemo } from 'react';

interface ConnectionLines3DProps {
  positions: Array<[number, number, number]>;
  color?: number;
  opacity?: number;
}

export default function ConnectionLines3D({
  positions,
  color = 0xff00ff,
  opacity = 0.6,
}: ConnectionLines3DProps) {
  const lineGeometries = useMemo(() => {
    const geometries: THREE.BufferGeometry[] = [];
    
    for (let i = 0; i < positions.length - 1; i++) {
      const points = [
        new THREE.Vector3(...positions[i]),
        new THREE.Vector3(...positions[i + 1]),
      ];
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      geometries.push(geometry);
    }
    
    return geometries;
  }, [positions]);

  return (
    <group>
      {lineGeometries.map((geometry, index) => (
        <line key={index} geometry={geometry}>
          <lineBasicMaterial
            color={color}
            transparent
            opacity={opacity}
          />
        </line>
      ))}
    </group>
  );
}
