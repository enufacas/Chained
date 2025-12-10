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
    // Set up fog for depth effect
    scene.fog = new THREE.FogExp2(0x0a0e1a, 0.012);
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

      {/* Ambient Light */}
      <ambientLight intensity={0.3} />

      {/* Hemisphere Light for better ambient */}
      <hemisphereLight
        color={0x0099ff}
        groundColor={0xff0099}
        intensity={0.4}
      />

      {/* Main Directional Light with shadows */}
      <directionalLight
        position={[30, 40, 20]}
        intensity={1.5}
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

      {/* Accent Point Lights */}
      <pointLight position={[25, 20, 25]} color={0x00ffff} intensity={2} distance={100} castShadow />
      <pointLight position={[-25, -10, -25]} color={0xff00ff} intensity={2} distance={100} castShadow />
      <pointLight position={[0, 30, 0]} color={0xffaa00} intensity={1.5} distance={80} />
    </>
  );
}
