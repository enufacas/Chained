import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * ProceduralRobotModel - Procedurally generated low-poly robot
 * Inspired by Quaternius and Kenney.nl aesthetic
 * 
 * @param {string} variant - Robot style: 'worker', 'scientist', 'analyst', 'engineer', 'writer', 'artist'
 * @param {string} state - Animation state: 'idle', 'processing', 'completed', 'failed'
 * @param {number} color - Hex color for robot
 * @param {boolean} isSelected - Selection state
 */
function ProceduralRobotModel({ 
  variant = 'worker',
  state = 'idle',
  color = 0x60a5fa,
  isSelected = false
}) {
  const groupRef = useRef();
  const headRef = useRef();
  const leftArmRef = useRef();
  const rightArmRef = useRef();
  const antennaRef = useRef();
  
  // Robot geometry based on variant
  const robotGeometry = useMemo(() => {
    const variants = {
      worker: {
        headSize: [0.8, 0.8, 0.8],
        bodySize: [1, 1.2, 0.6],
        legHeight: 0.8,
        hasAntenna: true,
        antennaHeight: 0.4
      },
      scientist: {
        headSize: [0.9, 0.9, 0.9],
        bodySize: [0.9, 1.1, 0.5],
        legHeight: 0.9,
        hasAntenna: true,
        antennaHeight: 0.6
      },
      analyst: {
        headSize: [0.85, 0.7, 0.85],
        bodySize: [0.95, 1, 0.55],
        legHeight: 0.85,
        hasAntenna: true,
        antennaHeight: 0.3
      },
      engineer: {
        headSize: [0.75, 0.9, 0.75],
        bodySize: [1.1, 1.3, 0.7],
        legHeight: 0.7,
        hasAntenna: false,
        antennaHeight: 0
      },
      writer: {
        headSize: [0.7, 0.8, 0.7],
        bodySize: [0.85, 1, 0.5],
        legHeight: 1,
        hasAntenna: true,
        antennaHeight: 0.5
      },
      artist: {
        headSize: [0.8, 0.85, 0.8],
        bodySize: [0.9, 1.1, 0.55],
        legHeight: 0.9,
        hasAntenna: true,
        antennaHeight: 0.7
      }
    };
    
    return variants[variant] || variants.worker;
  }, [variant]);
  
  // Animation based on state
  useFrame((state, delta) => {
    if (!groupRef.current) return;
    
    const time = state.clock.elapsedTime;
    
    if (state === 'idle') {
      // Gentle floating bob
      groupRef.current.position.y = Math.sin(time * 0.5) * 0.1;
      
      // Slight head tilt
      if (headRef.current) {
        headRef.current.rotation.y = Math.sin(time * 0.3) * 0.1;
      }
      
      // Antenna sway
      if (antennaRef.current && robotGeometry.hasAntenna) {
        antennaRef.current.rotation.z = Math.sin(time * 1.5) * 0.15;
      }
    } else if (state === 'processing') {
      // Faster bobbing
      groupRef.current.position.y = Math.sin(time * 2) * 0.15;
      groupRef.current.rotation.y += delta * 0.5;
      
      // Working arms motion
      if (leftArmRef.current && rightArmRef.current) {
        leftArmRef.current.rotation.x = Math.sin(time * 4) * 0.5 - 0.3;
        rightArmRef.current.rotation.x = Math.sin(time * 4 + Math.PI) * 0.5 - 0.3;
      }
      
      // Active head movement
      if (headRef.current) {
        headRef.current.rotation.y = Math.sin(time * 2) * 0.3;
      }
      
      // Antenna active
      if (antennaRef.current && robotGeometry.hasAntenna) {
        antennaRef.current.rotation.z = Math.sin(time * 3) * 0.3;
      }
    } else if (state === 'completed') {
      // Celebration bounce
      groupRef.current.position.y = Math.abs(Math.sin(time * 3)) * 0.3;
      
      // Arms up
      if (leftArmRef.current && rightArmRef.current) {
        leftArmRef.current.rotation.x = -1.5;
        rightArmRef.current.rotation.x = -1.5;
      }
    } else if (state === 'failed') {
      // Sad slump
      groupRef.current.rotation.z = Math.sin(time * 1) * 0.05;
      
      // Head down
      if (headRef.current) {
        headRef.current.rotation.x = 0.3;
      }
      
      // Arms down
      if (leftArmRef.current && rightArmRef.current) {
        leftArmRef.current.rotation.x = 0.5;
        rightArmRef.current.rotation.x = 0.5;
      }
    }
  });
  
  // Material with emissive glow
  const emissiveIntensity = useMemo(() => {
    if (isSelected) return 1.0;
    if (state === 'processing') return 0.8;
    if (state === 'completed') return 0.6;
    if (state === 'failed') return 0.3;
    return 0.2;
  }, [isSelected, state]);
  
  const emissiveColor = useMemo(() => {
    if (state === 'completed') return 0x4ade80; // Green
    if (state === 'failed') return 0xef4444; // Red
    if (state === 'processing') return 0xfbbf24; // Amber
    return color;
  }, [state, color]);
  
  return (
    <group ref={groupRef}>
      {/* Body */}
      <mesh position={[0, 0, 0]} castShadow>
        <boxGeometry args={robotGeometry.bodySize} />
        <meshStandardMaterial 
          color={color}
          emissive={emissiveColor}
          emissiveIntensity={emissiveIntensity}
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>
      
      {/* Head */}
      <mesh ref={headRef} position={[0, robotGeometry.bodySize[1] * 0.5 + robotGeometry.headSize[1] * 0.5, 0]} castShadow>
        <boxGeometry args={robotGeometry.headSize} />
        <meshStandardMaterial 
          color={color}
          emissive={emissiveColor}
          emissiveIntensity={emissiveIntensity * 1.2}
          metalness={0.9}
          roughness={0.1}
        />
      </mesh>
      
      {/* Eyes */}
      <mesh position={[-0.25, robotGeometry.bodySize[1] * 0.5 + robotGeometry.headSize[1] * 0.5, robotGeometry.headSize[2] * 0.5 + 0.05]}>
        <sphereGeometry args={[0.1, 8, 8]} />
        <meshStandardMaterial 
          color={0xffffff}
          emissive={emissiveColor}
          emissiveIntensity={2}
        />
      </mesh>
      <mesh position={[0.25, robotGeometry.bodySize[1] * 0.5 + robotGeometry.headSize[1] * 0.5, robotGeometry.headSize[2] * 0.5 + 0.05]}>
        <sphereGeometry args={[0.1, 8, 8]} />
        <meshStandardMaterial 
          color={0xffffff}
          emissive={emissiveColor}
          emissiveIntensity={2}
        />
      </mesh>
      
      {/* Antenna (if has) */}
      {robotGeometry.hasAntenna && (
        <group ref={antennaRef} position={[0, robotGeometry.bodySize[1] * 0.5 + robotGeometry.headSize[1] + robotGeometry.antennaHeight * 0.5, 0]}>
          <mesh castShadow>
            <cylinderGeometry args={[0.05, 0.05, robotGeometry.antennaHeight, 8]} />
            <meshStandardMaterial 
              color={color}
              emissive={emissiveColor}
              emissiveIntensity={emissiveIntensity * 1.5}
              metalness={1}
              roughness={0}
            />
          </mesh>
          <mesh position={[0, robotGeometry.antennaHeight * 0.5, 0]}>
            <sphereGeometry args={[0.1, 8, 8]} />
            <meshStandardMaterial 
              color={0xffffff}
              emissive={emissiveColor}
              emissiveIntensity={3}
            />
          </mesh>
        </group>
      )}
      
      {/* Left Arm */}
      <group ref={leftArmRef} position={[-robotGeometry.bodySize[0] * 0.5 - 0.15, robotGeometry.bodySize[1] * 0.3, 0]}>
        <mesh castShadow>
          <boxGeometry args={[0.2, 0.8, 0.2]} />
          <meshStandardMaterial 
            color={color}
            emissive={emissiveColor}
            emissiveIntensity={emissiveIntensity * 0.8}
            metalness={0.7}
            roughness={0.3}
          />
        </mesh>
        <mesh position={[0, -0.5, 0]} castShadow>
          <boxGeometry args={[0.25, 0.25, 0.25]} />
          <meshStandardMaterial 
            color={color}
            emissive={emissiveColor}
            emissiveIntensity={emissiveIntensity}
            metalness={0.6}
            roughness={0.4}
          />
        </mesh>
      </group>
      
      {/* Right Arm */}
      <group ref={rightArmRef} position={[robotGeometry.bodySize[0] * 0.5 + 0.15, robotGeometry.bodySize[1] * 0.3, 0]}>
        <mesh castShadow>
          <boxGeometry args={[0.2, 0.8, 0.2]} />
          <meshStandardMaterial 
            color={color}
            emissive={emissiveColor}
            emissiveIntensity={emissiveIntensity * 0.8}
            metalness={0.7}
            roughness={0.3}
          />
        </mesh>
        <mesh position={[0, -0.5, 0]} castShadow>
          <boxGeometry args={[0.25, 0.25, 0.25]} />
          <meshStandardMaterial 
            color={color}
            emissive={emissiveColor}
            emissiveIntensity={emissiveIntensity}
            metalness={0.6}
            roughness={0.4}
          />
        </mesh>
      </group>
      
      {/* Left Leg */}
      <mesh position={[-robotGeometry.bodySize[0] * 0.25, -robotGeometry.bodySize[1] * 0.5 - robotGeometry.legHeight * 0.5, 0]} castShadow>
        <boxGeometry args={[0.3, robotGeometry.legHeight, 0.3]} />
        <meshStandardMaterial 
          color={color}
          emissive={emissiveColor}
          emissiveIntensity={emissiveIntensity * 0.6}
          metalness={0.7}
          roughness={0.3}
        />
      </mesh>
      
      {/* Right Leg */}
      <mesh position={[robotGeometry.bodySize[0] * 0.25, -robotGeometry.bodySize[1] * 0.5 - robotGeometry.legHeight * 0.5, 0]} castShadow>
        <boxGeometry args={[0.3, robotGeometry.legHeight, 0.3]} />
        <meshStandardMaterial 
          color={color}
          emissive={emissiveColor}
          emissiveIntensity={emissiveIntensity * 0.6}
          metalness={0.7}
          roughness={0.3}
        />
      </mesh>
      
      {/* Feet */}
      <mesh position={[-robotGeometry.bodySize[0] * 0.25, -robotGeometry.bodySize[1] * 0.5 - robotGeometry.legHeight - 0.1, 0.15]} castShadow>
        <boxGeometry args={[0.35, 0.2, 0.5]} />
        <meshStandardMaterial 
          color={color}
          emissive={emissiveColor}
          emissiveIntensity={emissiveIntensity * 0.5}
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>
      <mesh position={[robotGeometry.bodySize[0] * 0.25, -robotGeometry.bodySize[1] * 0.5 - robotGeometry.legHeight - 0.1, 0.15]} castShadow>
        <boxGeometry args={[0.35, 0.2, 0.5]} />
        <meshStandardMaterial 
          color={color}
          emissive={emissiveColor}
          emissiveIntensity={emissiveIntensity * 0.5}
          metalness={0.8}
          roughness={0.2}
        />
      </mesh>
    </group>
  );
}

export default ProceduralRobotModel;
