import { useGLTF, useAnimations } from '@react-three/drei';
import { useEffect, useRef, useMemo } from 'react';
import * as THREE from 'three';

/**
 * AnimatedAgentModel - Wrapper for GLTF models with state-driven animations
 * 
 * @param {string} url - Path to GLTF/GLB model
 * @param {array} position - [x, y, z] position
 * @param {string} state - Agent state (idle, processing, completed, failed)
 * @param {number} color - Hex color for emissive glow
 * @param {boolean} isSelected - Whether agent is selected
 * @param {number} scale - Model scale
 */
function AnimatedAgentModel({ 
  url, 
  position = [0, 0, 0], 
  state = 'idle',
  color = 0x4a9eff,
  isSelected = false,
  scale = 0.5
}) {
  const group = useRef();
  const { scene, animations } = useGLTF(url);
  const { actions, names } = useAnimations(animations, group);
  
  // Clone the scene to allow multiple instances
  const clonedScene = useMemo(() => scene.clone(), [scene]);
  
  // Animation state mapping
  const animationMap = useMemo(() => ({
    idle: names[0] || 'idle',
    processing: names[1] || 'work',
    completed: names[2] || 'success',
    failed: names[3] || 'error'
  }), [names]);
  
  // Handle animation transitions based on state
  useEffect(() => {
    if (!actions || Object.keys(actions).length === 0) return;
    
    const targetAnimation = animationMap[state];
    
    // Fade out all animations
    Object.values(actions).forEach(action => {
      if (action) action.fadeOut(0.5);
    });
    
    // Fade in and play target animation
    if (actions[targetAnimation]) {
      actions[targetAnimation]
        .reset()
        .fadeIn(0.5)
        .play();
      
      // Loop based on state
      if (state === 'completed' || state === 'failed') {
        actions[targetAnimation].setLoop(THREE.LoopOnce);
        actions[targetAnimation].clampWhenFinished = true;
      } else {
        actions[targetAnimation].setLoop(THREE.LoopRepeat);
      }
    }
    
    return () => {
      if (actions[targetAnimation]) {
        actions[targetAnimation].fadeOut(0.5);
      }
    };
  }, [state, actions, animationMap]);
  
  // Apply emissive glow based on state and selection
  useEffect(() => {
    clonedScene.traverse((child) => {
      if (child.isMesh) {
        // Store original emissive if not already stored
        if (!child.userData.originalEmissive) {
          child.userData.originalEmissive = child.material.emissive.clone();
        }
        
        // Apply state-based emissive
        let emissiveIntensity = 0;
        let emissiveColor = new THREE.Color(color);
        
        if (isSelected) {
          emissiveIntensity = 0.8;
        } else if (state === 'processing') {
          emissiveIntensity = 0.6;
          emissiveColor = new THREE.Color(0xfbbf24); // Amber
        } else if (state === 'completed') {
          emissiveIntensity = 0.4;
          emissiveColor = new THREE.Color(0x4ade80); // Green
        } else if (state === 'failed') {
          emissiveIntensity = 0.4;
          emissiveColor = new THREE.Color(0xef4444); // Red
        }
        
        child.material.emissive = emissiveColor;
        child.material.emissiveIntensity = emissiveIntensity;
      }
    });
  }, [clonedScene, color, isSelected, state]);
  
  return (
    <group ref={group} position={position}>
      <primitive object={clonedScene} scale={scale} castShadow receiveShadow />
    </group>
  );
}

// Preload common models
export function preloadAgentModels() {
  const modelPaths = [
    '/models/agents/scientist.glb',
    '/models/agents/analyst.glb',
    '/models/agents/writer.glb',
    '/models/agents/developer.glb',
    '/models/agents/engineer.glb',
    '/models/agents/artist.glb'
  ];
  
  modelPaths.forEach(path => {
    useGLTF.preload(path);
  });
}

export default AnimatedAgentModel;
