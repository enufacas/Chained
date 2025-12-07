import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * ProceduralRoboticArm - Industrial robotic arm
 */
export function ProceduralRoboticArm({ position = [0, 0, 0], isActive = false }) {
  const baseRef = useRef();
  const arm1Ref = useRef();
  const arm2Ref = useRef();
  const gripperRef = useRef();
  
  useFrame((state) => {
    if (!isActive) {
      // Idle position
      if (arm1Ref.current) arm1Ref.current.rotation.z = 0;
      if (arm2Ref.current) arm2Ref.current.rotation.z = 0;
      if (gripperRef.current) {
        gripperRef.current.children[0].position.x = -0.1;
        gripperRef.current.children[1].position.x = 0.1;
      }
      return;
    }
    
    const time = state.clock.elapsedTime;
    
    // Working motion
    if (baseRef.current) {
      baseRef.current.rotation.y = Math.sin(time * 0.5) * 0.5;
    }
    if (arm1Ref.current) {
      arm1Ref.current.rotation.z = Math.sin(time * 0.7) * 0.3 + 0.5;
    }
    if (arm2Ref.current) {
      arm2Ref.current.rotation.z = Math.sin(time * 0.7 + Math.PI) * 0.3 - 0.5;
    }
    
    // Gripper open/close
    if (gripperRef.current) {
      const openAmount = (Math.sin(time * 2) + 1) * 0.1 + 0.05;
      gripperRef.current.children[0].position.x = -openAmount;
      gripperRef.current.children[1].position.x = openAmount;
    }
  });
  
  return (
    <group position={position}>
      {/* Base */}
      <group ref={baseRef}>
        <mesh position={[0, 0.5, 0]} castShadow>
          <cylinderGeometry args={[0.8, 1, 1, 16]} />
          <meshStandardMaterial 
            color="#3a6d9e"
            metalness={0.9}
            roughness={0.1}
          />
        </mesh>
        
        {/* Arm 1 */}
        <group ref={arm1Ref} position={[0, 1, 0]}>
          <mesh position={[0, 1, 0]} castShadow>
            <boxGeometry args={[0.4, 2, 0.4]} />
            <meshStandardMaterial 
              color="#4a9eff"
              metalness={0.8}
              roughness={0.2}
            />
          </mesh>
          
          {/* Joint */}
          <mesh position={[0, 2, 0]}>
            <sphereGeometry args={[0.3, 16, 16]} />
            <meshStandardMaterial 
              color="#2a4d6e"
              metalness={1}
              roughness={0}
            />
          </mesh>
          
          {/* Arm 2 */}
          <group ref={arm2Ref} position={[0, 2, 0]}>
            <mesh position={[0, 1, 0]} castShadow>
              <boxGeometry args={[0.35, 2, 0.35]} />
              <meshStandardMaterial 
                color="#60a5fa"
                metalness={0.8}
                roughness={0.2}
              />
            </mesh>
            
            {/* Gripper */}
            <group ref={gripperRef} position={[0, 2, 0]}>
              <mesh position={[-0.1, 0, 0]} castShadow>
                <boxGeometry args={[0.1, 0.5, 0.2]} />
                <meshStandardMaterial 
                  color="#8fe3ff"
                  metalness={0.7}
                  roughness={0.3}
                />
              </mesh>
              <mesh position={[0.1, 0, 0]} castShadow>
                <boxGeometry args={[0.1, 0.5, 0.2]} />
                <meshStandardMaterial 
                  color="#8fe3ff"
                  metalness={0.7}
                  roughness={0.3}
                />
              </mesh>
            </group>
          </group>
        </group>
      </group>
      
      {/* Activity indicator lights */}
      {isActive && (
        <>
          <pointLight position={[0, 3, 0]} color="#fbbf24" intensity={2} distance={5} />
          <mesh position={[0, 0.5, 0]}>
            <sphereGeometry args={[0.2, 8, 8]} />
            <meshStandardMaterial 
              color="#fbbf24"
              emissive="#fbbf24"
              emissiveIntensity={2}
            />
          </mesh>
        </>
      )}
    </group>
  );
}

/**
 * ProceduralConveyorBelt - Moving conveyor belt
 */
export function ProceduralConveyorBelt({ position = [0, 0, 0], speed = 1, length = 20 }) {
  const beltRef = useRef();
  
  useFrame((state, delta) => {
    if (beltRef.current && speed > 0) {
      beltRef.current.position.z += delta * speed * 2;
      if (beltRef.current.position.z > 2) {
        beltRef.current.position.z = -2;
      }
    }
  });
  
  return (
    <group position={position}>
      {/* Belt structure */}
      <mesh position={[0, 0.2, 0]} receiveShadow>
        <boxGeometry args={[2, 0.3, length]} />
        <meshStandardMaterial 
          color="#2a3142"
          metalness={0.5}
          roughness={0.8}
        />
      </mesh>
      
      {/* Moving belt surface */}
      <group ref={beltRef}>
        {Array.from({ length: Math.ceil(length / 2) }).map((_, i) => (
          <mesh key={i} position={[0, 0.36, i * 2 - length / 2]}>
            <boxGeometry args={[1.8, 0.05, 1.5]} />
            <meshStandardMaterial 
              color="#3a4556"
              metalness={0.3}
              roughness={0.9}
            />
          </mesh>
        ))}
      </group>
      
      {/* Rollers */}
      {[-length / 2 + 1, length / 2 - 1].map((z, i) => (
        <mesh key={i} position={[0, 0, z]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.3, 0.3, 2.2, 16]} />
          <meshStandardMaterial 
            color="#4a5568"
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>
      ))}
    </group>
  );
}

/**
 * ProceduralDrone - Flying surveillance drone
 */
export function ProceduralDrone({ position = [0, 10, 0], path = null }) {
  const groupRef = useRef();
  const propellerRefs = [useRef(), useRef(), useRef(), useRef()];
  
  useFrame((state, delta) => {
    const time = state.clock.elapsedTime;
    
    // Hover motion
    if (groupRef.current) {
      groupRef.current.position.y = position[1] + Math.sin(time * 1.5) * 0.5;
      groupRef.current.rotation.x = Math.sin(time * 0.5) * 0.05;
      groupRef.current.rotation.z = Math.cos(time * 0.5) * 0.05;
    }
    
    // Spin propellers
    propellerRefs.forEach(ref => {
      if (ref.current) {
        ref.current.rotation.y += delta * 30;
      }
    });
  });
  
  return (
    <group ref={groupRef} position={position}>
      {/* Body */}
      <mesh castShadow>
        <boxGeometry args={[0.8, 0.3, 0.8]} />
        <meshStandardMaterial 
          color="#4a9eff"
          metalness={0.9}
          roughness={0.1}
        />
      </mesh>
      
      {/* Camera/sensor */}
      <mesh position={[0, -0.3, 0]}>
        <sphereGeometry args={[0.15, 16, 16]} />
        <meshStandardMaterial 
          color="#000000"
          metalness={1}
          roughness={0}
        />
      </mesh>
      
      {/* Propeller arms and propellers */}
      {[[-0.5, 0, -0.5], [0.5, 0, -0.5], [-0.5, 0, 0.5], [0.5, 0, 0.5]].map((pos, i) => (
        <group key={i} position={pos}>
          {/* Arm */}
          <mesh position={[0, 0.2, 0]}>
            <cylinderGeometry args={[0.05, 0.05, 0.4, 8]} />
            <meshStandardMaterial 
              color="#2a4d6e"
              metalness={0.8}
              roughness={0.2}
            />
          </mesh>
          
          {/* Propeller */}
          <group ref={propellerRefs[i]} position={[0, 0.45, 0]}>
            <mesh>
              <boxGeometry args={[0.6, 0.02, 0.1]} />
              <meshStandardMaterial 
                color="#60a5fa"
                metalness={0.7}
                roughness={0.3}
                transparent
                opacity={0.7}
              />
            </mesh>
            <mesh rotation={[0, Math.PI / 2, 0]}>
              <boxGeometry args={[0.6, 0.02, 0.1]} />
              <meshStandardMaterial 
                color="#60a5fa"
                metalness={0.7}
                roughness={0.3}
                transparent
                opacity={0.7}
              />
            </mesh>
          </group>
        </group>
      ))}
      
      {/* Light indicator */}
      <pointLight position={[0, 0, 0]} color="#4ade80" intensity={1} distance={3} />
      <mesh position={[0, 0.2, 0]}>
        <sphereGeometry args={[0.08, 8, 8]} />
        <meshStandardMaterial 
          color="#4ade80"
          emissive="#4ade80"
          emissiveIntensity={2}
        />
      </mesh>
    </group>
  );
}

/**
 * ProceduralDataPod - Holographic data container
 */
export function ProceduralDataPod({ position = [0, 0, 0], isTransferring = false }) {
  const groupRef = useRef();
  const innerRef = useRef();
  
  useFrame((state) => {
    const time = state.clock.elapsedTime;
    
    if (groupRef.current) {
      groupRef.current.rotation.y = time * 0.5;
    }
    
    if (innerRef.current) {
      innerRef.current.rotation.y = -time * 1;
      innerRef.current.rotation.x = time * 0.7;
      
      if (isTransferring) {
        const pulse = Math.sin(time * 4) * 0.2 + 1;
        innerRef.current.scale.set(pulse, pulse, pulse);
      }
    }
  });
  
  return (
    <group ref={groupRef} position={position}>
      {/* Outer container */}
      <mesh>
        <octahedronGeometry args={[0.5, 0]} />
        <meshStandardMaterial 
          color="#4a9eff"
          metalness={0.9}
          roughness={0.1}
          transparent
          opacity={0.3}
          wireframe
        />
      </mesh>
      
      {/* Inner core */}
      <group ref={innerRef}>
        <mesh>
          <icosahedronGeometry args={[0.3, 0]} />
          <meshStandardMaterial 
            color={isTransferring ? "#fbbf24" : "#6dd5ff"}
            emissive={isTransferring ? "#fbbf24" : "#6dd5ff"}
            emissiveIntensity={isTransferring ? 2 : 1}
            metalness={0.8}
            roughness={0.2}
            transparent
            opacity={0.8}
          />
        </mesh>
      </group>
      
      {/* Particles */}
      {isTransferring && (
        <>
          {Array.from({ length: 20 }).map((_, i) => {
            const angle = (i / 20) * Math.PI * 2;
            const radius = 0.8;
            return (
              <mesh 
                key={i} 
                position={[
                  Math.cos(angle) * radius,
                  Math.sin(angle * 2) * 0.3,
                  Math.sin(angle) * radius
                ]}
              >
                <sphereGeometry args={[0.05, 8, 8]} />
                <meshStandardMaterial 
                  color="#fbbf24"
                  emissive="#fbbf24"
                  emissiveIntensity={2}
                />
              </mesh>
            );
          })}
        </>
      )}
      
      {/* Point light */}
      <pointLight 
        color={isTransferring ? "#fbbf24" : "#6dd5ff"}
        intensity={isTransferring ? 3 : 1.5}
        distance={5}
      />
    </group>
  );
}

/**
 * ProceduralFactoryEnvironment - Complete procedural environment
 */
export function ProceduralFactoryEnvironment({ activePipeline = false }) {
  return (
    <group>
      {/* Robotic arms at cardinal points */}
      <ProceduralRoboticArm position={[30, 0, 0]} isActive={activePipeline} />
      <ProceduralRoboticArm position={[-30, 0, 0]} isActive={activePipeline} />
      <ProceduralRoboticArm position={[0, 0, 30]} isActive={activePipeline} />
      <ProceduralRoboticArm position={[0, 0, -30]} isActive={activePipeline} />
      
      {/* Conveyor belts */}
      <ProceduralConveyorBelt 
        position={[0, -2, -25]} 
        speed={activePipeline ? 1 : 0.3}
        length={15}
      />
      <ProceduralConveyorBelt 
        position={[0, -2, 25]} 
        speed={activePipeline ? 1 : 0.3}
        length={15}
      />
      
      {/* Hovering drones */}
      <ProceduralDrone position={[15, 12, 15]} />
      <ProceduralDrone position={[-15, 15, -15]} />
      <ProceduralDrone position={[0, 18, 0]} />
      
      {/* Data pods during transfer */}
      {activePipeline && (
        <>
          <ProceduralDataPod position={[10, 5, 0]} isTransferring={true} />
          <ProceduralDataPod position={[-10, 5, 0]} isTransferring={true} />
          <ProceduralDataPod position={[0, 8, 10]} isTransferring={true} />
        </>
      )}
    </group>
  );
}

export default ProceduralFactoryEnvironment;
