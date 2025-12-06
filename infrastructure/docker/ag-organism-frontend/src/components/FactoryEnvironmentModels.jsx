import { useGLTF, useAnimations } from '@react-three/drei';
import { useEffect, useRef } from 'react';

/**
 * RoboticArm - Animated robotic arm for factory environment
 */
function RoboticArm({ position = [0, 0, 0], isActive = false }) {
  const group = useRef();
  const { scene, animations } = useGLTF('/models/environment/robotic-arm.glb');
  const { actions } = useAnimations(animations, group);
  
  useEffect(() => {
    if (isActive && actions['work']) {
      actions['work'].play();
    } else if (actions['idle']) {
      actions['idle'].play();
    }
  }, [isActive, actions]);
  
  return (
    <group ref={group} position={position}>
      <primitive object={scene.clone()} scale={2} castShadow receiveShadow />
    </group>
  );
}

/**
 * ConveyorBelt - Animated conveyor belt
 */
function ConveyorBelt({ position = [0, -2, 0], speed = 1 }) {
  const group = useRef();
  const { scene, animations } = useGLTF('/models/environment/conveyor.glb');
  const { actions } = useAnimations(animations, group);
  
  useEffect(() => {
    if (actions['run']) {
      actions['run'].setTimeScale(speed).play();
    }
  }, [actions, speed]);
  
  return (
    <group ref={group} position={position}>
      <primitive object={scene.clone()} scale={1.5} receiveShadow />
    </group>
  );
}

/**
 * HoverDrone - Animated flying drone
 */
function HoverDrone({ position = [0, 10, 0], path = null }) {
  const group = useRef();
  const { scene, animations } = useGLTF('/models/environment/drone.glb');
  const { actions } = useAnimations(animations, group);
  
  useEffect(() => {
    if (actions['hover']) {
      actions['hover'].play();
    }
  }, [actions]);
  
  // TODO: Add path following logic if path is provided
  
  return (
    <group ref={group} position={position}>
      <primitive object={scene.clone()} scale={0.8} castShadow />
    </group>
  );
}

/**
 * DataPod - Animated holographic data container
 */
function DataPod({ position = [0, 0, 0], isTransferring = false }) {
  const group = useRef();
  const { scene, animations } = useGLTF('/models/environment/data-pod.glb');
  const { actions } = useAnimations(animations, group);
  
  useEffect(() => {
    const animName = isTransferring ? 'transfer' : 'idle';
    if (actions[animName]) {
      Object.values(actions).forEach(a => a?.stop());
      actions[animName].play();
    }
  }, [isTransferring, actions]);
  
  return (
    <group ref={group} position={position}>
      <primitive object={scene.clone()} scale={0.5} />
    </group>
  );
}

/**
 * FactoryEnvironmentModels - Collection of animated environmental elements
 */
function FactoryEnvironmentModels({ activePipeline = false }) {
  return (
    <group>
      {/* Robotic arms at cardinal points */}
      <RoboticArm position={[30, 0, 0]} isActive={activePipeline} />
      <RoboticArm position={[-30, 0, 0]} isActive={activePipeline} />
      <RoboticArm position={[0, 0, 30]} isActive={activePipeline} />
      <RoboticArm position={[0, 0, -30]} isActive={activePipeline} />
      
      {/* Conveyor belts */}
      <ConveyorBelt position={[0, -2, -20]} speed={activePipeline ? 1 : 0.3} />
      <ConveyorBelt position={[0, -2, 20]} speed={activePipeline ? 1 : 0.3} />
      
      {/* Hovering drones */}
      <HoverDrone position={[15, 12, 15]} />
      <HoverDrone position={[-15, 15, -15]} />
      <HoverDrone position={[0, 18, 0]} />
      
      {/* Data pods (shown during transfer) */}
      {activePipeline && (
        <>
          <DataPod position={[10, 5, 0]} isTransferring={true} />
          <DataPod position={[-10, 5, 0]} isTransferring={true} />
        </>
      )}
    </group>
  );
}

// Preload environmental models
export function preloadEnvironmentModels() {
  const paths = [
    '/models/environment/robotic-arm.glb',
    '/models/environment/conveyor.glb',
    '/models/environment/drone.glb',
    '/models/environment/data-pod.glb'
  ];
  
  paths.forEach(path => {
    useGLTF.preload(path);
  });
}

export {
  RoboticArm,
  ConveyorBelt,
  HoverDrone,
  DataPod,
  FactoryEnvironmentModels
};

export default FactoryEnvironmentModels;
