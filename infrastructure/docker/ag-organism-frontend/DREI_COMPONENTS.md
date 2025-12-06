# Drei Components Guide for AG-Organism

## Overview

AG-Organism now leverages advanced components from [@react-three/drei](https://github.com/pmndrs/drei), the premier helper library for React Three Fiber. This document explains which Drei components are used and how to extend them.

**Reference**: https://drei.pmnd.rs/

---

## Currently Implemented Drei Components

### 1. MeshReflectorMaterial

**Purpose**: Creates realistic reflections on the factory platform floor.

**Location**: `Scene3D.jsx` → `FactoryPlatform` component

**Usage:**
```jsx
<mesh receiveShadow rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.5, 0]}>
  <circleGeometry args={[26, 64]} />
  <MeshReflectorMaterial
    blur={[400, 100]}
    resolution={512}
    mixBlur={0.8}
    mixStrength={20}
    roughness={0.5}
    depthScale={0.8}
    minDepthThreshold={0.5}
    maxDepthThreshold={1.2}
    color="#2a3142"
    metalness={0.8}
  />
</mesh>
```

**Key Parameters:**
- `resolution`: 512px (lower = better performance)
- `blur`: [400, 100] horizontal and vertical blur
- `mixStrength`: 20 (reflection intensity)
- `metalness`: 0.8 (metallic look)

**Performance Tips:**
- Lower resolution for mobile (256px)
- Reduce mixStrength if too glossy
- Increase blur for softer reflections

---

### 2. Sparkles

**Purpose**: Animated particle effects representing data flow.

**Location**: `Scene3D.jsx` → `EnhancedParticles` component

**Usage:**
```jsx
function EnhancedParticles() {
  return (
    <>
      {/* Main sparkles cloud */}
      <Sparkles
        count={100}
        scale={[35, 20, 35]}
        size={2}
        speed={0.3}
        opacity={0.6}
        color="#4a9eff"
      />
      
      {/* Secondary sparkles for depth */}
      <Sparkles
        count={50}
        scale={[25, 15, 25]}
        size={1.5}
        speed={0.5}
        opacity={0.4}
        color="#6dd5ff"
      />
      
      {/* Accent sparkles */}
      <Sparkles
        count={30}
        scale={[20, 10, 20]}
        size={3}
        speed={0.2}
        opacity={0.8}
        color="#8fe3ff"
      />
    </>
  );
}
```

**Key Parameters:**
- `count`: Number of particles
- `scale`: [x, y, z] bounding box
- `size`: Particle size
- `speed`: Animation speed (0-1)
- `color`: Hex color

**Customization Ideas:**
- Add more layers for denser effects
- Change colors to match agent states
- Adjust speed based on activity level
- Scale particles during pipeline execution

---

### 3. Float

**Purpose**: Smooth organic floating animation for agents.

**Location**: `Scene3D.jsx` → wrapping `AgentHumanoid` components

**Usage:**
```jsx
<Float
  key={agent.id}
  speed={1.5}
  rotationIntensity={state === 'processing' ? 0.5 : 0.1}
  floatIntensity={0.5}
  floatingRange={[-0.5, 0.5]}
>
  <group>
    <AgentHumanoid agent={agent} position={position} />
    <AgentLabel text={agent.displayName} position={position} />
  </group>
</Float>
```

**Key Parameters:**
- `speed`: Animation speed (default: 1)
- `rotationIntensity`: Rotation amount (0-1)
- `floatIntensity`: Float amount (0-1)
- `floatingRange`: [min, max] Y-axis range

**State-Based Animation:**
- Idle: Low rotation (0.1)
- Processing: Higher rotation (0.5)
- Can add more states (completed, failed)

**Benefits:**
- Replaces manual `useFrame` animation
- Smoother motion with easing
- Less code to maintain
- Automatic performance optimization

---

### 4. ContactShadows

**Purpose**: Realistic soft shadows beneath agents for depth perception.

**Location**: `Scene3D.jsx` → main scene

**Usage:**
```jsx
<ContactShadows
  position={[0, -2.4, 0]}
  opacity={0.5}
  scale={50}
  blur={2}
  far={10}
  resolution={256}
  color="#4a9eff"
/>
```

**Key Parameters:**
- `position`: Ground plane position
- `opacity`: Shadow darkness (0-1)
- `scale`: Coverage area
- `blur`: Shadow softness
- `far`: Shadow distance
- `resolution`: Quality (256/512/1024)
- `color`: Tint color

**Customization:**
- Increase opacity for darker shadows
- Reduce blur for sharper edges
- Change color to match lighting
- Adjust position for platform height

---

### 5. Grid

**Purpose**: Industrial factory floor grid.

**Location**: `Scene3D.jsx` → main scene

**Usage:**
```jsx
<Grid
  position={[0, -2.5, 0]}
  args={[100, 100]}
  cellSize={2}
  cellThickness={0.5}
  cellColor="#2a4d6e"
  sectionSize={10}
  sectionThickness={1}
  sectionColor="#3a6d9e"
  fadeDistance={80}
  fadeStrength={1}
  infiniteGrid={false}
/>
```

**Key Parameters:**
- `args`: [width, height]
- `cellSize`: Unit size
- `sectionSize`: Major grid sections
- `cellColor`/`sectionColor`: Colors
- `fadeDistance`: Fade start distance
- `infiniteGrid`: Infinite or bounded

---

### 6. OrbitControls

**Purpose**: Camera navigation.

**Location**: `Scene3D.jsx` → main scene

**Usage:**
```jsx
<DreiOrbitControls
  ref={controlsRef}
  enableDamping
  dampingFactor={0.05}
  minDistance={20}
  maxDistance={100}
  args={[camera, gl.domElement]}
/>
```

---

## Additional Drei Components to Consider

### Text3D
3D text labels instead of CSS3D.

```jsx
import { Text3D, Center } from '@react-three/drei'

<Center>
  <Text3D font="/fonts/helvetiker_regular.typeface.json" size={0.5}>
    Agent Name
    <meshStandardMaterial color="#4a9eff" />
  </Text3D>
</Center>
```

### Trail
Motion trails behind moving objects.

```jsx
import { Trail } from '@react-three/drei'

<Trail width={2} length={6} color="#4a9eff" attenuation={(t) => t * t}>
  <AgentHumanoid />
</Trail>
```

### Glow
Add glow effect to agents.

```jsx
import { Glow } from '@react-three/drei'

<mesh>
  <sphereGeometry />
  <meshBasicMaterial>
    <Glow damping={6} intensity={0.5} scale={1.2} />
  </meshBasicMaterial>
</mesh>
```

### Backdrop
Background curtain effect.

```jsx
import { Backdrop } from '@react-three/drei'

<Backdrop
  floor={0.25}
  segments={20}
  scale={[30, 10, 10]}
  position={[0, -2, -5]}
>
  <meshStandardMaterial color="#2a3142" />
</Backdrop>
```

### CameraShake
Add camera shake during events.

```jsx
import { CameraShake } from '@react-three/drei'

<CameraShake
  maxYaw={0.01}
  maxPitch={0.01}
  maxRoll={0.01}
  yawFrequency={0.5}
  pitchFrequency={0.5}
  rollFrequency={0.5}
/>
```

### Sky
Replace fog with procedural sky.

```jsx
import { Sky } from '@react-three/drei'

<Sky
  distance={450000}
  sunPosition={[0, 1, 0]}
  inclination={0}
  azimuth={0.25}
/>
```

### Stars
Add starfield background.

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

---

## Performance Best Practices

### Resolution Settings
- **Desktop**: 512-1024px for reflections
- **Mobile**: 256-512px for reflections
- **Shadows**: 256px resolution

### Particle Counts
- **Desktop**: 150-200 sparkles total
- **Mobile**: 50-100 sparkles total

### Optimization Checklist
- [ ] Use lower resolutions on mobile
- [ ] Reduce particle counts for performance
- [ ] Disable expensive effects if FPS drops
- [ ] Use `fog` to hide far objects
- [ ] Limit shadow-casting objects

---

## Custom Drei Component Creation

You can create custom Drei-style components:

```jsx
function CustomFactoryElement() {
  const ref = useRef()
  
  useFrame((state, delta) => {
    ref.current.rotation.y += delta * 0.5
  })
  
  return (
    <Float speed={2} floatIntensity={1}>
      <mesh ref={ref}>
        <torusGeometry args={[2, 0.5, 16, 100]} />
        <MeshReflectorMaterial
          color="#4a9eff"
          metalness={0.9}
          roughness={0.1}
        />
      </mesh>
    </Float>
  )
}
```

---

## Debugging Drei Components

### Common Issues

**1. Environment preset fails to load:**
- Remove `Environment` component or don't use external presets
- Use manual lighting instead

**2. Reflections not showing:**
- Check `resolution` (must be power of 2: 256, 512, 1024)
- Ensure objects are within `minDepthThreshold` range
- Verify camera is looking at reflective surface

**3. Sparkles not visible:**
- Check `opacity` (should be 0.5-1.0)
- Verify `scale` encompasses the scene
- Ensure `color` contrasts with background

**4. Float not animating:**
- Must wrap a `<group>` or `<mesh>`
- Check `floatIntensity` and `speed` values
- Ensure inside `<Canvas>`

---

## Testing New Drei Components

1. **Check Drei documentation**: https://drei.pmnd.rs/
2. **Add import**: `import { ComponentName } from '@react-three/drei'`
3. **Test in Scene3D.jsx** first
4. **Monitor performance** (FPS, memory)
5. **Adjust parameters** for factory theme
6. **Document in this file**

---

## Component Combinations

### Factory Machine Effect
```jsx
<Float speed={1}>
  <group>
    <mesh>
      <boxGeometry args={[2, 2, 2]} />
      <MeshReflectorMaterial color="#4a9eff" metalness={0.9} />
    </mesh>
    <Sparkles count={20} scale={3} color="#6dd5ff" />
  </group>
</Float>
```

### Glowing Agent
```jsx
<Float>
  <group>
    <AgentHumanoid />
    <Sparkles count={10} scale={2} size={1} />
    <pointLight color="#4a9eff" intensity={2} distance={5} />
  </group>
</Float>
```

---

## Version History

- **v2.1.0** (2025-12-06) - Added Drei components (Sparkles, Float, ContactShadows, MeshReflectorMaterial)
- **v2.0.0** (2025-12-06) - Initial R3F migration with basic Drei (Grid, OrbitControls)

---

## Resources

- **Drei Docs**: https://drei.pmnd.rs/
- **Drei GitHub**: https://github.com/pmndrs/drei
- **Drei Examples**: https://drei.pmnd.rs/?path=/story/staging-stage--stage-st
- **R3F Docs**: https://r3f.docs.pmnd.rs/
