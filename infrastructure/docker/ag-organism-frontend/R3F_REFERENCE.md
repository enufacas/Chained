# React Three Fiber (R3F) Reference Guide

## Overview
This document provides a reference for React Three Fiber patterns and examples from the official documentation at https://r3f.docs.pmnd.rs/getting-started/examples

**Purpose**: Quick reference for implementing and iterating on AG-Organism 3D features using R3F best practices.

---

## Table of Contents
1. [Core Concepts](#core-concepts)
2. [Common Patterns](#common-patterns)
3. [Performance Optimization](#performance-optimization)
4. [Interactive Examples](#interactive-examples)
5. [Post-Processing Effects](#post-processing-effects)
6. [Animation Techniques](#animation-techniques)
7. [AG-Organism Specific Usage](#ag-organism-specific-usage)

---

## Core Concepts

### Basic Canvas Setup
```jsx
import { Canvas } from '@react-three/fiber'

function App() {
  return (
    <Canvas
      camera={{ position: [0, 0, 5], fov: 75 }}
      gl={{ antialias: true, alpha: true }}
      shadows
    >
      {/* 3D content here */}
    </Canvas>
  )
}
```

### Mesh Components
```jsx
function Box(props) {
  return (
    <mesh {...props}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="orange" />
    </mesh>
  )
}
```

### Hooks
- **`useFrame(callback)`** - Runs on every frame (animation loop)
- **`useThree()`** - Access to Three.js context (camera, scene, gl, etc.)
- **`useLoader()`** - Asset loading
- **`useGraph()`** - GLTF scene graph traversal

---

## Common Patterns

### 1. Animation with useFrame
```jsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

function RotatingBox() {
  const meshRef = useRef()
  
  useFrame((state, delta) => {
    meshRef.current.rotation.x += delta
    meshRef.current.rotation.y += delta * 0.5
  })
  
  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial color="hotpink" />
    </mesh>
  )
}
```

**AG-Organism Usage**: Agent humanoid floating animation, rotation during processing state

### 2. Interactive Objects (Pointer Events)
```jsx
function InteractiveSphere() {
  const [hovered, setHovered] = useState(false)
  const [active, setActive] = useState(false)
  
  return (
    <mesh
      scale={active ? 1.5 : 1}
      onClick={() => setActive(!active)}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      <sphereGeometry />
      <meshStandardMaterial color={hovered ? 'hotpink' : 'orange'} />
    </mesh>
  )
}
```

**AG-Organism Usage**: Click to select agents, hover effects for agent cards

### 3. OrbitControls (from drei)
```jsx
import { OrbitControls } from '@react-three/drei'

function Scene() {
  return (
    <>
      <OrbitControls
        enableDamping
        dampingFactor={0.05}
        minDistance={20}
        maxDistance={100}
      />
      {/* Other scene content */}
    </>
  )
}
```

**AG-Organism Usage**: Camera navigation around agent circle

---

## Performance Optimization

### 1. Instance Rendering (Multiple Similar Objects)
```jsx
import { Instance, Instances } from '@react-three/drei'

function Particles() {
  return (
    <Instances limit={1000}>
      <sphereGeometry args={[0.1]} />
      <meshStandardMaterial />
      {Array.from({ length: 1000 }).map((_, i) => (
        <Instance key={i} position={[Math.random() * 10, Math.random() * 10, Math.random() * 10]} />
      ))}
    </Instances>
  )
}
```

**AG-Organism Potential**: If we add particle effects or multiple similar artifacts

### 2. Level of Detail (LOD)
```jsx
import { Detailed } from '@react-three/drei'

function LODModel() {
  return (
    <Detailed distances={[0, 10, 20]}>
      <HighQualityModel />      {/* distance 0-10 */}
      <MediumQualityModel />     {/* distance 10-20 */}
      <LowQualityModel />        {/* distance > 20 */}
    </Detailed>
  )
}
```

### 3. Memoization
```jsx
import { useMemo } from 'react'

function OptimizedComponent() {
  const geometry = useMemo(() => new THREE.SphereGeometry(1, 32, 32), [])
  const material = useMemo(() => new THREE.MeshStandardMaterial({ color: 'red' }), [])
  
  return <mesh geometry={geometry} material={material} />
}
```

**AG-Organism Usage**: Agent humanoid geometries can be memoized since they don't change

---

## Interactive Examples

### 1. Floating Effect
```jsx
function FloatingObject() {
  const meshRef = useRef()
  
  useFrame(({ clock }) => {
    meshRef.current.position.y = Math.sin(clock.elapsedTime) * 0.5
  })
  
  return (
    <mesh ref={meshRef}>
      <boxGeometry />
      <meshStandardMaterial />
    </mesh>
  )
}
```

**AG-Organism Usage**: ✅ Already implemented for agent humanoids

### 2. Following Mouse/Pointer
```jsx
function FollowPointer() {
  const meshRef = useRef()
  
  useFrame(({ pointer, viewport }) => {
    const x = (pointer.x * viewport.width) / 2
    const y = (pointer.y * viewport.height) / 2
    meshRef.current.position.x = THREE.MathUtils.lerp(meshRef.current.position.x, x, 0.1)
    meshRef.current.position.y = THREE.MathUtils.lerp(meshRef.current.position.y, y, 0.1)
  })
  
  return <mesh ref={meshRef}>...</mesh>
}
```

### 3. Click to Spawn
```jsx
function SpawnOnClick() {
  const [objects, setObjects] = useState([])
  
  const handleClick = (e) => {
    setObjects([...objects, { id: Date.now(), position: e.point }])
  }
  
  return (
    <>
      <mesh onClick={handleClick}>
        <planeGeometry args={[100, 100]} />
        <meshBasicMaterial visible={false} />
      </mesh>
      {objects.map(obj => (
        <Box key={obj.id} position={obj.position} />
      ))}
    </>
  )
}
```

**AG-Organism Potential**: Click to create artifacts or messages in 3D space

---

## Post-Processing Effects

### Using @react-three/postprocessing
```jsx
import { EffectComposer, Bloom, DepthOfField, Noise, Vignette } from '@react-three/postprocessing'

function Scene() {
  return (
    <Canvas>
      {/* 3D content */}
      <EffectComposer>
        <Bloom
          intensity={1.5}
          luminanceThreshold={0.9}
          luminanceSmoothing={0.9}
        />
        <DepthOfField focusDistance={0.01} focalLength={0.2} bokehScale={2} />
        <Noise opacity={0.02} />
        <Vignette eskil={false} offset={0.1} darkness={1.1} />
      </EffectComposer>
    </Canvas>
  )
}
```

**AG-Organism Usage**: ✅ Bloom effect implemented, can add more effects

### Selective Bloom (Bloom on Specific Objects)
```jsx
import { BloomEffect, KernelSize } from 'postprocessing'

// Mark objects for bloom with layers
<mesh layers={1}>
  <meshStandardMaterial emissive="cyan" emissiveIntensity={2} />
</mesh>

// Configure bloom to only affect layer 1
<EffectComposer>
  <Bloom layers={[1]} intensity={1.5} />
</EffectComposer>
```

**AG-Organism Potential**: Bloom only on active/processing agents

---

## Animation Techniques

### 1. Spring Animations (with react-spring)
```jsx
import { useSpring, animated } from '@react-spring/three'

function AnimatedBox() {
  const [active, setActive] = useState(false)
  
  const { scale } = useSpring({
    scale: active ? 1.5 : 1,
    config: { mass: 1, tension: 170, friction: 26 }
  })
  
  return (
    <animated.mesh scale={scale} onClick={() => setActive(!active)}>
      <boxGeometry />
      <meshStandardMaterial />
    </animated.mesh>
  )
}
```

**AG-Organism Potential**: Smooth scale transitions when selecting agents

### 2. GSAP Integration
```jsx
import gsap from 'gsap'

function GSAPAnimation() {
  const meshRef = useRef()
  
  useEffect(() => {
    gsap.to(meshRef.current.position, {
      y: 5,
      duration: 2,
      repeat: -1,
      yoyo: true,
      ease: "power1.inOut"
    })
  }, [])
  
  return <mesh ref={meshRef}>...</mesh>
}
```

### 3. Keyframe Animations
```jsx
function KeyframeAnimation() {
  const meshRef = useRef()
  
  useFrame(({ clock }) => {
    const t = (clock.elapsedTime % 4) / 4 // 0 to 1 over 4 seconds
    
    if (t < 0.25) {
      meshRef.current.position.x = THREE.MathUtils.lerp(0, 5, t * 4)
    } else if (t < 0.5) {
      meshRef.current.position.y = THREE.MathUtils.lerp(0, 5, (t - 0.25) * 4)
    } else if (t < 0.75) {
      meshRef.current.position.x = THREE.MathUtils.lerp(5, 0, (t - 0.5) * 4)
    } else {
      meshRef.current.position.y = THREE.MathUtils.lerp(5, 0, (t - 0.75) * 4)
    }
  })
  
  return <mesh ref={meshRef}>...</mesh>
}
```

**AG-Organism Potential**: Agent movement during task handoff

---

## AG-Organism Specific Usage

### Current Implementation Patterns

#### 1. Agent Humanoid Component
```jsx
// src/components/AgentHumanoid.jsx
function AgentHumanoid({ position, color, agentId, status }) {
  const groupRef = useRef()
  const floatOffset = useMemo(() => Math.random() * Math.PI * 2, [])
  
  // Floating animation
  useFrame(({ clock }) => {
    if (groupRef.current) {
      groupRef.current.position.y = Math.sin(clock.elapsedTime * 0.02 + floatOffset) * 1
      
      // Rotate when processing
      if (status === 'processing') {
        groupRef.current.rotation.y += 0.02
      }
    }
  })
  
  return (
    <group ref={groupRef} position={position}>
      {/* Humanoid parts */}
    </group>
  )
}
```

#### 2. Scene Setup with Lighting
```jsx
// src/components/Scene3D.jsx
<Canvas
  camera={{ position: [0, 15, 40], fov: 75 }}
  gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
  shadows
>
  {/* Lighting */}
  <ambientLight intensity={0.3} />
  <directionalLight position={[30, 40, 20]} intensity={1.5} castShadow />
  <pointLight position={[25, 20, 25]} color="#00ffff" intensity={2} distance={100} />
  <pointLight position={[-25, -10, -25]} color="#ff00ff" intensity={2} distance={100} />
  
  {/* Controls */}
  <OrbitControls
    enableDamping
    dampingFactor={0.05}
    minDistance={20}
    maxDistance={100}
  />
  
  {/* Fog */}
  <fog attach="fog" args={['#0a0e1a', 20, 100]} />
  
  {/* Content */}
  <Suspense fallback={null}>
    {agents.map(agent => (
      <AgentHumanoid key={agent.id} {...agent} />
    ))}
  </Suspense>
  
  {/* Post-processing */}
  <PostProcessing />
</Canvas>
```

#### 3. Dynamic Content Updates
```jsx
// Update agents based on API responses
useEffect(() => {
  if (pipelineData?.a2aSteps) {
    pipelineData.a2aSteps.forEach(step => {
      setAgents(prev => prev.map(agent =>
        agent.id === step.agentName
          ? { ...agent, status: step.status?.state }
          : agent
      ))
    })
  }
}, [pipelineData])
```

---

## Useful Drei Helpers

### 1. Text3D
```jsx
import { Text3D } from '@react-three/drei'

<Text3D font="/fonts/helvetiker_regular.typeface.json" size={0.5}>
  Hello World
  <meshStandardMaterial color="hotpink" />
</Text3D>
```

**AG-Organism Potential**: 3D labels instead of CSS3D

### 2. Html (HTML Overlay)
```jsx
import { Html } from '@react-three/drei'

<mesh>
  <boxGeometry />
  <meshStandardMaterial />
  <Html position={[0, 1, 0]} center>
    <div className="label">Agent Name</div>
  </Html>
</mesh>
```

**AG-Organism Usage**: ✅ Currently using for agent labels

### 3. Environment Lighting
```jsx
import { Environment } from '@react-three/drei'

<Environment preset="city" background={false} />
// Presets: sunset, dawn, night, warehouse, forest, apartment, studio, city, park, lobby
```

**AG-Organism Potential**: Replace manual light setup with preset

### 4. Sky
```jsx
import { Sky } from '@react-three/drei'

<Sky
  distance={450000}
  sunPosition={[0, 1, 0]}
  inclination={0}
  azimuth={0.25}
/>
```

### 5. Stars
```jsx
import { Stars } from '@react-three/drei'

<Stars
  radius={100}
  depth={50}
  count={5000}
  factor={4}
  saturation={0}
  fade
  speed={1}
/>
```

**AG-Organism Potential**: Cyberpunk space background

### 6. Grid Helper
```jsx
import { Grid } from '@react-three/drei'

<Grid
  args={[10, 10]}
  cellSize={1}
  cellThickness={0.5}
  cellColor="#6f6f6f"
  sectionSize={5}
  sectionThickness={1.5}
  sectionColor="#9d4b4b"
  fadeDistance={50}
  fadeStrength={1}
/>
```

---

## Advanced Patterns

### 1. Raycasting for Custom Interactions
```jsx
import { useThree } from '@react-three/fiber'

function CustomRaycaster() {
  const { camera, scene } = useThree()
  const raycaster = useMemo(() => new THREE.Raycaster(), [])
  
  const handleClick = (event) => {
    const pointer = new THREE.Vector2(
      (event.clientX / window.innerWidth) * 2 - 1,
      -(event.clientY / window.innerHeight) * 2 + 1
    )
    
    raycaster.setFromCamera(pointer, camera)
    const intersects = raycaster.intersectObjects(scene.children, true)
    
    if (intersects.length > 0) {
      console.log('Hit:', intersects[0].object)
    }
  }
  
  return <group onClick={handleClick}>...</group>
}
```

### 2. Custom Shaders
```jsx
import { shaderMaterial } from '@react-three/drei'
import { extend } from '@react-three/fiber'

const CustomMaterial = shaderMaterial(
  { uTime: 0, uColor: new THREE.Color(0.0, 0.0, 0.0) },
  // Vertex shader
  `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  // Fragment shader
  `
    uniform float uTime;
    uniform vec3 uColor;
    varying vec2 vUv;
    void main() {
      gl_FragColor = vec4(uColor * sin(uTime + vUv.x * 10.0), 1.0);
    }
  `
)

extend({ CustomMaterial })

function ShaderMesh() {
  const materialRef = useRef()
  
  useFrame(({ clock }) => {
    materialRef.current.uTime = clock.elapsedTime
  })
  
  return (
    <mesh>
      <planeGeometry args={[2, 2]} />
      <customMaterial ref={materialRef} uColor={[1, 0, 0]} />
    </mesh>
  )
}
```

**AG-Organism Potential**: Custom shader effects for connections or agent auras

---

## Performance Best Practices

### 1. Frustum Culling (Automatic)
Objects outside camera view are automatically not rendered.

### 2. Dispose on Unmount
```jsx
useEffect(() => {
  return () => {
    // R3F handles most cleanup automatically, but for custom resources:
    myTexture.dispose()
    myGeometry.dispose()
    myMaterial.dispose()
  }
}, [])
```

**AG-Organism**: ✅ R3F handles this automatically for standard components

### 3. Lazy Loading
```jsx
import { Suspense } from 'react'
import { useGLTF } from '@react-three/drei'

function Model() {
  const { scene } = useGLTF('/model.glb')
  return <primitive object={scene} />
}

function Scene() {
  return (
    <Suspense fallback={<Loader />}>
      <Model />
    </Suspense>
  )
}
```

### 4. Reduce Draw Calls
- Merge geometries when possible
- Use instancing for repeated objects
- Reuse materials and geometries

---

## Resources

### Official Documentation
- Main Docs: https://r3f.docs.pmnd.rs/
- Examples: https://r3f.docs.pmnd.rs/getting-started/examples
- API Reference: https://r3f.docs.pmnd.rs/api/canvas
- GitHub: https://github.com/pmndrs/react-three-fiber

### Drei Helpers
- Documentation: https://github.com/pmndrs/drei
- Storybook: https://drei.pmnd.rs/

### Post-Processing
- Documentation: https://github.com/pmndrs/react-postprocessing
- Effects List: https://github.com/pmndrs/postprocessing#effects

### Learning Resources
- Three.js Journey: https://threejs-journey.com/
- Three.js Fundamentals: https://threejs.org/manual/
- R3F Discord: https://discord.gg/poimandres

---

## Next Steps for AG-Organism

### Potential Enhancements

1. **Better Animations**
   - Add spring animations for agent selection
   - Smooth transitions between states
   - Particle trails for data flow

2. **Visual Effects**
   - Selective bloom on active agents
   - Glow pulses during processing
   - Data streams between agents (animated particles)
   - Custom shaders for agent auras

3. **Performance**
   - Instance rendering if adding many similar objects
   - LOD for complex models
   - Optimize for mobile

4. **Interactivity**
   - Click agents in 3D to select (not just sidebar)
   - Drag-and-drop agent arrangement
   - Zoom to agent on selection

5. **Environment**
   - Add cyberpunk background (stars, grid, fog)
   - Dynamic lighting based on agent activity
   - Environment map for reflections

6. **Data Visualization**
   - 3D graphs for metrics
   - Flow visualization for A2A messages
   - Timeline scrubbing

---

## Version History
- **v1.0** (2025-12-06): Initial reference document created during R3F migration
- Repository: `/home/runner/work/Chained/Chained/infrastructure/docker/ag-organism-frontend/`
- Current R3F version: 8.15.16
- Current Drei version: 9.96.1
