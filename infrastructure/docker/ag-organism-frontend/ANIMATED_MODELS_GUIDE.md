# Animated 3D Models Guide for AG-Organism

## Overview

This guide covers options for incorporating animated 3D models into the AG-Organism scene using React Three Fiber and Drei components.

---

## Model Format Options

### 1. GLTF/GLB (Recommended)

**Best Choice For**: Complex animated models, character rigs, skeletal animations

**Advantages:**
- Industry standard (supported everywhere)
- Compact binary format (GLB)
- Supports animations, morphs, PBR materials
- Excellent Drei support via `useGLTF` and `useAnimations`
- Can include multiple animations per model

**File Size**: 100KB - 5MB typical

**Example Sources:**
- [Sketchfab](https://sketchfab.com/3d-models?features=downloadable&sort_by=-likeCount) - Free downloadable models
- [Mixamo](https://www.mixamo.com/) - Free rigged characters with animations
- [Poly Pizza](https://poly.pizza/) - Free low-poly models
- [Quaternius](http://quaternius.com/) - Free game-ready models
- [KennyNL](https://www.kenney.nl/assets) - Free assets

---

## Implementation Options

### Option 1: useGLTF + useAnimations (Recommended)

**Best For**: Full control over animations, complex character models

```jsx
import { useGLTF, useAnimations } from '@react-three/drei'
import { useEffect, useRef } from 'react'

function AnimatedRobot({ position, state }) {
  const group = useRef()
  const { scene, animations } = useGLTF('/models/robot.glb')
  const { actions, names } = useAnimations(animations, group)
  
  // Play animation based on state
  useEffect(() => {
    const animationMap = {
      idle: 'Idle',
      processing: 'Working',
      completed: 'Success',
      failed: 'Error'
    }
    
    const animName = animationMap[state] || 'Idle'
    
    // Fade out current animations
    Object.values(actions).forEach(action => action?.fadeOut(0.5))
    
    // Fade in new animation
    actions[animName]?.reset().fadeIn(0.5).play()
    
    return () => actions[animName]?.fadeOut(0.5)
  }, [state, actions])
  
  return (
    <group ref={group} position={position}>
      <primitive object={scene} scale={0.5} />
    </group>
  )
}

// Preload the model
useGLTF.preload('/models/robot.glb')
```

**Key Features:**
- Smooth animation transitions (fadeIn/fadeOut)
- State-driven animation selection
- Automatic cleanup
- Preloading for better performance

---

### Option 2: Clone from Drei Library

**Best For**: Quick prototyping with included Drei models

```jsx
import { Clone } from '@react-three/drei'
import { useGLTF } from '@react-three/drei'

function FactoryBot({ position }) {
  const { scene } = useGLTF('/models/bot.glb')
  
  return (
    <Clone 
      object={scene} 
      position={position}
      scale={0.5}
      castShadow
      receiveShadow
    />
  )
}
```

**Advantages:**
- Reuses geometry (efficient)
- Easy instancing for multiple copies
- Good for repeated elements

---

### Option 3: AnimatedModel Component (Custom Wrapper)

**Best For**: Consistent API across different model types

```jsx
import { useGLTF, useAnimations } from '@react-three/drei'
import { useEffect, useRef } from 'react'

function AnimatedModel({ 
  url, 
  position = [0, 0, 0], 
  scale = 1,
  animation = 'idle',
  autoPlay = true 
}) {
  const group = useRef()
  const { scene, animations } = useGLTF(url)
  const { actions, mixer } = useAnimations(animations, group)
  
  useEffect(() => {
    if (autoPlay && actions[animation]) {
      actions[animation].reset().play()
    }
  }, [animation, actions, autoPlay])
  
  return (
    <group ref={group} position={position}>
      <primitive object={scene} scale={scale} />
    </group>
  )
}

// Usage
<AnimatedModel 
  url="/models/robot.glb" 
  position={[0, 0, 0]}
  animation="walk"
  scale={0.5}
/>
```

---

## AG-Organism Integration Patterns

### Pattern 1: Replace Agent Humanoids

Replace current capsule-based humanoids with animated models:

```jsx
// In AgentHumanoid.jsx
import AnimatedAgentModel from './AnimatedAgentModel'

function AgentHumanoid({ agent, position, state }) {
  // Map agent types to models
  const modelMap = {
    'academic-research': '/models/scientist.glb',
    'google-trends': '/models/analyst.glb',
    'blog-writer': '/models/writer.glb',
    'code-reviewer': '/models/developer.glb',
    'data-analyst': '/models/engineer.glb',
    'image-generator': '/models/artist.glb'
  }
  
  return (
    <AnimatedAgentModel
      url={modelMap[agent.id]}
      position={position}
      state={state}
      color={getAgentColor(agent.id)}
    />
  )
}
```

---

### Pattern 2: Add Animated Props/Environment

Add animated environmental elements:

```jsx
// Animated factory machines
function FactoryMachines() {
  return (
    <>
      {/* Robotic arms */}
      <AnimatedModel 
        url="/models/robotic-arm.glb"
        position={[15, 0, 0]}
        animation="work"
        scale={2}
      />
      
      {/* Conveyor belt */}
      <AnimatedModel 
        url="/models/conveyor.glb"
        position={[-15, -2, 0]}
        animation="run"
        scale={1.5}
      />
      
      {/* Factory drones */}
      <AnimatedModel 
        url="/models/drone.glb"
        position={[0, 10, 10]}
        animation="hover"
        scale={0.8}
      />
    </>
  )
}
```

---

### Pattern 3: Background Characters/Robots

Add ambient animated elements:

```jsx
function BackgroundBots() {
  const bots = [
    { pos: [20, 0, 20], anim: 'walk', delay: 0 },
    { pos: [-20, 0, -20], anim: 'patrol', delay: 2 },
    { pos: [0, 0, -25], anim: 'idle', delay: 4 }
  ]
  
  return (
    <>
      {bots.map((bot, i) => (
        <AnimatedModel
          key={i}
          url="/models/security-bot.glb"
          position={bot.pos}
          animation={bot.anim}
          scale={0.6}
        />
      ))}
    </>
  )
}
```

---

## Recommended Models for AG-Organism

### 1. Low-Poly Robot Characters

**Style**: Factory workers, each representing an agent type

**Sources:**
- Quaternius Ultimate Modular Characters
- Kenney Robotics Kit
- Poly Pizza robots

**Animations Needed:**
- Idle
- Working/Typing
- Success celebration
- Error/Confused

**File Size**: ~500KB per character (optimized)

---

### 2. Industrial Machines

**Style**: Animated factory equipment

**Examples:**
- Robotic arms (welding, assembling)
- Conveyor belts
- Overhead cranes
- Assembly lines

**Sources:**
- Sketchfab industrial category
- Free3D machinery section

**Animations Needed:**
- Continuous operation loops
- On/off states

---

### 3. Flying Drones/Vehicles

**Style**: Data carriers, moving between agents

**Examples:**
- Quadcopter drones
- Hover platforms
- Data pods

**Animations Needed:**
- Hover/float
- Propeller rotation
- Travel paths

---

### 4. Holographic Elements

**Style**: Futuristic UI, data visualizations

**Examples:**
- Spinning holograms
- Data streams
- Progress indicators

**Implementation:**
- Can use emissive materials
- Transparent with glow
- Animated UVs or morph targets

---

## Performance Considerations

### Model Optimization

**File Size Targets:**
- Per agent model: &lt; 500KB
- Environmental props: &lt; 1MB each
- Total scene: &lt; 10MB

**Optimization Tools:**
- [gltf-pipeline](https://github.com/CesiumGS/gltf-pipeline) - Compression
- [glTF-Transform](https://gltf-transform.donmccurdy.com/) - Optimization
- Blender GLTF exporter with Draco compression

**Optimization Checklist:**
- [ ] Use Draco compression
- [ ] Limit texture resolution (512x512 or 1024x1024)
- [ ] Remove unused animations
- [ ] Simplify geometry (&lt;10K triangles per model)
- [ ] Use texture atlases
- [ ] Merge materials where possible

---

### Loading Strategy

**Progressive Loading:**

```jsx
import { Suspense } from 'react'
import { Html, useProgress } from '@react-three/drei'

function Loader() {
  const { progress } = useProgress()
  return (
    <Html center>
      <div style={{ color: '#4a9eff', fontSize: '24px' }}>
        Loading {progress.toFixed(0)}%
      </div>
    </Html>
  )
}

function Scene() {
  return (
    <Suspense fallback={<Loader />}>
      <AnimatedAgents />
      <FactoryEnvironment />
    </Suspense>
  )
}
```

**Preloading:**

```jsx
// Preload all models on app init
const models = [
  '/models/agent-1.glb',
  '/models/agent-2.glb',
  '/models/factory-prop.glb'
]

models.forEach(url => useGLTF.preload(url))
```

---

## Animation System Architecture

### Centralized Animation Manager

```jsx
// AnimationManager.js
const ANIMATION_STATES = {
  idle: {
    loop: true,
    timeScale: 1,
    fadeTime: 0.5
  },
  processing: {
    loop: true,
    timeScale: 1.5,
    fadeTime: 0.3
  },
  completed: {
    loop: false,
    timeScale: 1,
    fadeTime: 0.2,
    onComplete: () => 'idle'
  },
  failed: {
    loop: false,
    timeScale: 1,
    fadeTime: 0.2,
    onComplete: () => 'idle'
  }
}

export function useStateAnimation(actions, state) {
  useEffect(() => {
    const config = ANIMATION_STATES[state]
    if (!config || !actions[state]) return
    
    // Stop all other animations
    Object.entries(actions).forEach(([name, action]) => {
      if (name !== state) {
        action?.fadeOut(config.fadeTime)
      }
    })
    
    // Play current animation
    const currentAction = actions[state]
    currentAction
      .reset()
      .setLoop(config.loop)
      .setTimeScale(config.timeScale)
      .fadeIn(config.fadeTime)
      .play()
    
    return () => currentAction?.fadeOut(config.fadeTime)
  }, [state, actions])
}
```

---

## Example Implementation

### Complete Agent with Animated Model

```jsx
import { useGLTF, useAnimations, Float } from '@react-three/drei'
import { useEffect, useRef } from 'react'
import { useStateAnimation } from './AnimationManager'

function AnimatedAgent({ agent, position, state, isSelected }) {
  const group = useRef()
  const { scene, animations } = useGLTF(agent.modelUrl)
  const { actions } = useAnimations(animations, group)
  
  // Handle animation based on state
  useStateAnimation(actions, state)
  
  // Add glow effect when selected
  useEffect(() => {
    scene.traverse((child) => {
      if (child.isMesh) {
        child.material.emissive.setHex(isSelected ? 0x4a9eff : 0x000000)
        child.material.emissiveIntensity = isSelected ? 0.5 : 0
      }
    })
  }, [isSelected, scene])
  
  return (
    <Float speed={1.5} floatIntensity={0.5}>
      <group ref={group} position={position}>
        <primitive object={scene} scale={0.5} />
        
        {/* Add particle effects */}
        {state === 'processing' && (
          <Sparkles count={20} scale={2} size={1} color="#4a9eff" />
        )}
      </group>
    </Float>
  )
}

export default AnimatedAgent
```

---

## Testing & Validation

### Model Testing Checklist

- [ ] Loads within 3 seconds
- [ ] Animations play smoothly (60fps)
- [ ] No console errors
- [ ] Proper scale relative to scene
- [ ] Materials render correctly
- [ ] Shadows work properly
- [ ] Mobile performance acceptable

### Browser Testing

Test on:
- Chrome (desktop)
- Firefox (desktop)
- Safari (desktop)
- Chrome (mobile)
- Safari (iOS)

---

## Quick Start Example

### 1. Download a Model

Visit [Sketchfab](https://sketchfab.com/3d-models?features=downloadable&sort_by=-likeCount) and download a free animated robot model.

### 2. Optimize It

```bash
npm install -g gltf-pipeline
gltf-pipeline -i robot.gltf -o robot.glb -d
```

### 3. Add to Project

Place in `/public/models/robot.glb`

### 4. Use in Scene

```jsx
import { useGLTF, useAnimations } from '@react-three/drei'

function Robot({ position }) {
  const { scene, animations } = useGLTF('/models/robot.glb')
  const { actions } = useAnimations(animations, group)
  
  useEffect(() => {
    actions[animations[0].name]?.play()
  }, [actions, animations])
  
  return (
    <group position={position}>
      <primitive object={scene} scale={0.5} />
    </group>
  )
}
```

---

## Advanced Features

### Mixed Animation Layers

Combine multiple animations:

```jsx
function AdvancedAgent({ state }) {
  const { actions } = useAnimations(animations, group)
  
  useEffect(() => {
    // Base layer: Always playing
    actions['body-idle']?.play()
    
    // Top layer: State-specific
    if (state === 'processing') {
      actions['arms-typing']?.play()
      actions['head-focus']?.play()
    }
  }, [state, actions])
}
```

### Dynamic Model Swapping

Change models at runtime:

```jsx
function DynamicAgent({ modelType, position }) {
  const [currentModel, setCurrentModel] = useState(modelType)
  
  return (
    <Suspense fallback={null}>
      <AnimatedModel 
        key={currentModel} 
        url={`/models/${currentModel}.glb`}
        position={position}
      />
    </Suspense>
  )
}
```

---

## Recommended Next Steps

1. **Choose Model Style**: Low-poly robots vs detailed characters
2. **Source Models**: Download 2-3 test models from Sketchfab/Mixamo
3. **Create AnimatedAgent Component**: Replace current humanoid system
4. **Add Environmental Props**: Conveyor belts, robotic arms
5. **Implement Animation System**: State-driven animation manager
6. **Optimize Performance**: Compress models, test on mobile
7. **Polish**: Add particle effects, glow, trails

---

## Resources

**Model Libraries:**
- https://sketchfab.com/
- https://www.mixamo.com/
- https://poly.pizza/
- http://quaternius.com/
- https://www.kenney.nl/assets

**Optimization Tools:**
- https://github.com/CesiumGS/gltf-pipeline
- https://gltf-transform.donmccurdy.com/
- https://products.aspose.app/3d/compress

**Documentation:**
- https://threejs.org/docs/#manual/en/introduction/Loading-3D-models
- https://drei.pmnd.rs/?path=/story/abstractions-gltf--use-gltf-st
- https://r3f.docs.pmnd.rs/tutorials/loading-models

---

**Version**: 1.0.0 (2025-12-06)
