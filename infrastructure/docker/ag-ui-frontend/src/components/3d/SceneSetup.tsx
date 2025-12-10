/**
 * SceneSetup Component
 * 
 * Sets up lighting, camera, and controls for the 3D scene
 * Matches the visual style from organism.html
 */

import { OrbitControls, PerspectiveCamera } from '@react-three/drei';
import { useThree } from '@react-three/fiber';
import { useEffect } from 'react';
import * as THREE from 'three';

export default function SceneSetup() {
  const { scene } = useThree();

  useEffect(() => {
    // Subtle fog for depth (slate-900 background color)
    scene.fog = new THREE.FogExp2(0x0f172a, 0.008);
  }, [scene]);

  return (
    <>
      {/* Camera */}
      <PerspectiveCamera makeDefault position={[0, 15, 40]} fov={75} />

      {/* Orbit Controls */}
      <OrbitControls
        enableDamping
        dampingFactor={0.05}
        minDistance={20}
        maxDistance={100}
        target={[0, 0, 0]}
      />

      {/* Ambient Light - general illumination */}
      <ambientLight intensity={0.4} />

      {/* Hemisphere Light - subtle gradient from top to bottom */}
      <hemisphereLight
        color={0xffffff}
        groundColor={0x334155}
        intensity={0.5}
      />

      {/* Main Directional Light with shadows - clean studio lighting */}
      <directionalLight
        position={[30, 40, 20]}
        intensity={1.2}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-near={0.5}
        shadow-camera-far={500}
        shadow-camera-left={-100}
        shadow-camera-right={100}
        shadow-camera-top={100}
        shadow-camera-bottom={-100}
      />

      {/* Fill lights - subtle, no strong colors */}
      <pointLight position={[20, 15, 20]} color={0xffffff} intensity={0.8} distance={80} />
      <pointLight position={[-20, 10, -20]} color={0xffffff} intensity={0.6} distance={80} />
    </>
  );
}
