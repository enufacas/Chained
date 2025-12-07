import { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { Text } from '@react-three/drei';

/**
 * A2AMessageVisualizer - Visualizes A2A protocol messages flowing between agents
 * Shows task handoffs, message exchanges, and protocol events
 */
export function A2AMessageVisualizer({ messages = [], agents = [] }) {
  const [activeMessages, setActiveMessages] = useState([]);
  
  useEffect(() => {
    setActiveMessages(messages.slice(-10)); // Keep last 10 messages
  }, [messages]);
  
  return (
    <group>
      {activeMessages.map((msg, idx) => (
        <A2AMessageParticle 
          key={msg.id || idx}
          message={msg}
          agents={agents}
          delay={idx * 0.1}
        />
      ))}
    </group>
  );
}

/**
 * Individual message particle that animates from source to target agent
 */
function A2AMessageParticle({ message, agents, delay = 0 }) {
  const groupRef = useRef();
  const [progress, setProgress] = useState(0);
  const [visible, setVisible] = useState(true);
  
  const sourceAgent = agents.find(a => a.id === message.from);
  const targetAgent = agents.find(a => a.id === message.to);
  
  const sourcePos = sourceAgent?.position || new THREE.Vector3(0, 0, 0);
  const targetPos = targetAgent?.position || new THREE.Vector3(0, 0, 0);
  
  useFrame((state, delta) => {
    if (!groupRef.current || !visible) return;
    
    const animationProgress = Math.min(1, progress + delta * 0.5);
    setProgress(animationProgress);
    
    if (animationProgress >= 1) {
      setTimeout(() => setVisible(false), 500);
      return;
    }
    
    // Interpolate position with arc
    const t = animationProgress;
    const eased = 1 - Math.pow(1 - t, 3); // Ease out cubic
    
    const x = THREE.MathUtils.lerp(sourcePos.x, targetPos.x, eased);
    const y = THREE.MathUtils.lerp(sourcePos.y, targetPos.y, eased) + Math.sin(eased * Math.PI) * 5;
    const z = THREE.MathUtils.lerp(sourcePos.z, targetPos.z, eased);
    
    groupRef.current.position.set(x, y, z);
    
    // Pulse animation
    const scale = 1 + Math.sin(state.clock.elapsedTime * 8) * 0.2;
    groupRef.current.scale.setScalar(scale);
    
    // Rotation
    groupRef.current.rotation.y += delta * 3;
  });
  
  if (!visible) return null;
  
  const color = message.type === 'task' ? '#fbbf24' : '#6dd5ff';
  
  return (
    <group ref={groupRef} position={[sourcePos.x, sourcePos.y, sourcePos.z]}>
      {/* Message particle */}
      <mesh>
        <octahedronGeometry args={[0.3, 0]} />
        <meshStandardMaterial 
          color={color}
          emissive={color}
          emissiveIntensity={2}
          transparent
          opacity={0.8}
        />
      </mesh>
      
      {/* Particle trail */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.15, 8, 8]} />
        <meshStandardMaterial 
          color={color}
          emissive={color}
          emissiveIntensity={1}
          transparent
          opacity={0.5}
        />
      </mesh>
      
      {/* Message text label (optional) */}
      {message.label && progress < 0.5 && (
        <Text
          position={[0, 1, 0]}
          fontSize={0.4}
          color="#ffffff"
          anchorX="center"
          anchorY="middle"
        >
          {message.label}
        </Text>
      )}
    </group>
  );
}

/**
 * Task status indicator that appears above processing agents
 */
export function A2ATaskIndicator({ agentId, taskStatus, position }) {
  const groupRef = useRef();
  
  useFrame((state) => {
    if (!groupRef.current) return;
    
    // Float animation
    groupRef.current.position.y = position.y + 4 + Math.sin(state.clock.elapsedTime * 2) * 0.3;
    
    // Rotation
    groupRef.current.rotation.y = state.clock.elapsedTime * 0.5;
  });
  
  const getStatusColor = () => {
    switch (taskStatus) {
      case 'pending': return '#94a3b8';
      case 'processing': return '#fbbf24';
      case 'completed': return '#4ade80';
      case 'failed': return '#ef4444';
      default: return '#60a5fa';
    }
  };
  
  const color = getStatusColor();
  
  return (
    <group ref={groupRef} position={[position.x, position.y + 4, position.z]}>
      {/* Status icon */}
      <mesh>
        <torusGeometry args={[0.8, 0.15, 16, 32]} />
        <meshStandardMaterial 
          color={color}
          emissive={color}
          emissiveIntensity={1.5}
        />
      </mesh>
      
      {/* Inner glow */}
      <mesh>
        <ringGeometry args={[0.4, 0.6, 16]} />
        <meshBasicMaterial 
          color={color}
          transparent
          opacity={0.6}
          side={THREE.DoubleSide}
        />
      </mesh>
      
      {/* Status text */}
      <Text
        position={[0, -1.5, 0]}
        fontSize={0.4}
        color={color}
        anchorX="center"
        anchorY="middle"
        outlineWidth={0.05}
        outlineColor="#000000"
      >
        {taskStatus.toUpperCase()}
      </Text>
    </group>
  );
}

/**
 * Data transfer effect between agents
 */
export function A2ADataTransfer({ fromPos, toPos, active = false }) {
  const linesRef = useRef();
  
  useFrame((state) => {
    if (!linesRef.current || !active) return;
    
    // Animate line dash
    linesRef.current.material.dashOffset -= 0.05;
  });
  
  if (!active) return null;
  
  const points = [
    new THREE.Vector3(fromPos.x, fromPos.y + 2, fromPos.z),
    new THREE.Vector3(
      (fromPos.x + toPos.x) / 2,
      Math.max(fromPos.y, toPos.y) + 5,
      (fromPos.z + toPos.z) / 2
    ),
    new THREE.Vector3(toPos.x, toPos.y + 2, toPos.z)
  ];
  
  const curve = new THREE.CatmullRomCurve3(points);
  const linePoints = curve.getPoints(50);
  const geometry = new THREE.BufferGeometry().setFromPoints(linePoints);
  
  return (
    <line ref={linesRef} geometry={geometry}>
      <lineDashedMaterial 
        color="#6dd5ff"
        dashSize={0.5}
        gapSize={0.3}
        linewidth={2}
        transparent
        opacity={0.8}
      />
    </line>
  );
}
