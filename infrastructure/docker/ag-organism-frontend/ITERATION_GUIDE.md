# AG-Organism Iteration Guide

## Quick Reference

This guide helps you iterate on the AG-Organism React Three Fiber implementation.

**Always refer to**: `R3F_REFERENCE.md` for detailed R3F patterns and examples.

---

## Development Workflow

### 1. Start Development Server
```bash
cd infrastructure/docker/ag-organism-frontend
npm install  # First time only
npm run dev  # Vite dev server with HMR
```
Open http://localhost:5173

### 2. Make Changes
Edit files in `src/`:
- **3D Components**: `src/components/AgentHumanoid.jsx`, `Scene3D.jsx`, etc.
- **UI Components**: `src/components/AgentPanel.jsx`, `Header.jsx`, etc.
- **Logic**: `src/api/agentApi.js`, `src/App.jsx`

Changes auto-reload thanks to Vite HMR.

### 3. Test Locally
```bash
npm run build    # Build for production
npm run serve    # Test production build
```
Open http://localhost:8080

### 4. Test in Docker
```bash
docker build -t ag-organism-test .
docker run -p 8080:8080 \
  -e NEXT_PUBLIC_ADK_API_URL=http://localhost:8080 \
  -e AG_UI_FRONTEND_URL=http://localhost:3000 \
  ag-organism-test
```

---

## Common Iterations

### Add New 3D Element

**Reference**: R3F_REFERENCE.md → [Common Patterns](#common-patterns)

1. Create component in `src/components/`
2. Use R3F declarative syntax:
```jsx
function NewElement() {
  return (
    <mesh position={[0, 0, 0]}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="cyan" />
    </mesh>
  )
}
```
3. Import in `Scene3D.jsx` and add to scene

### Add Animation

**Reference**: R3F_REFERENCE.md → [Animation Techniques](#animation-techniques)

```jsx
import { useRef } from 'react'
import { useFrame } from '@react-three/fiber'

function AnimatedElement() {
  const ref = useRef()
  
  useFrame((state, delta) => {
    ref.current.rotation.x += delta
  })
  
  return <mesh ref={ref}>...</mesh>
}
```

### Add Interaction

**Reference**: R3F_REFERENCE.md → [Interactive Examples](#interactive-examples)

```jsx
function InteractiveElement() {
  const [clicked, setClicked] = useState(false)
  
  return (
    <mesh
      onClick={() => setClicked(!clicked)}
      onPointerOver={() => console.log('hover')}
      scale={clicked ? 1.5 : 1}
    >
      <boxGeometry />
      <meshStandardMaterial color={clicked ? 'hotpink' : 'cyan'} />
    </mesh>
  )
}
```

### Add Post-Processing Effect

**Reference**: R3F_REFERENCE.md → [Post-Processing Effects](#post-processing-effects)

Edit `src/components/PostProcessing.jsx`:
```jsx
import { EffectComposer, Bloom, Vignette } from '@react-three/postprocessing'

export default function PostProcessing({ enabled }) {
  if (!enabled) return null
  
  return (
    <EffectComposer>
      <Bloom intensity={1.5} />
      <Vignette />  {/* Add new effect */}
    </EffectComposer>
  )
}
```

### Add UI Component

1. Create in `src/components/` with `.jsx` and `.css`
2. Import in `src/App.jsx`
3. Use React state for interactivity

Example:
```jsx
// src/components/NewPanel.jsx
import './NewPanel.css'

export default function NewPanel({ data }) {
  return (
    <div className="new-panel">
      <h3>Title</h3>
      <div>{data}</div>
    </div>
  )
}
```

---

## Project Structure

```
ag-organism-frontend/
├── src/
│   ├── main.jsx              # Entry point
│   ├── App.jsx               # Main app component
│   ├── App.css               # Main styles
│   ├── index.css             # Global styles
│   ├── api/
│   │   └── agentApi.js       # Backend API calls
│   └── components/
│       ├── Scene3D.jsx       # Main 3D scene with Canvas
│       ├── AgentHumanoid.jsx # 3D agent model
│       ├── AgentLabel.jsx    # CSS3D label
│       ├── ConnectionLines.jsx
│       ├── PostProcessing.jsx
│       ├── Header.jsx + .css
│       ├── AgentPanel.jsx + .css
│       ├── PromptPanel.jsx + .css
│       ├── ControlPanel.jsx + .css
│       └── LoadingScreen.jsx + .css
├── public/
│   └── assets/              # Static assets
├── index.html               # HTML entry
├── vite.config.js           # Vite configuration
├── package.json             # Dependencies
├── Dockerfile               # Multi-stage build
├── server.js                # Express production server
├── R3F_REFERENCE.md         # 👈 R3F examples reference
└── ITERATION_GUIDE.md       # 👈 This file
```

---

## Quick Tips

### Performance
- **Memoize geometries**: `useMemo(() => new THREE.SphereGeometry(), [])`
- **Reuse materials**: Share materials between meshes
- **Use `useFrame` sparingly**: Runs every frame (~60fps)
- **Dispose resources**: R3F handles most cleanup automatically

### Debugging
- **React DevTools**: Install extension to inspect component tree
- **R3F DevTools**: `<Canvas debugger />` for scene inspector
- **Console logs in useFrame**: Be careful, logs 60 times/second!
- **Three.js Inspector**: Browser extension for Three.js debugging

### Best Practices
- **Keep components small**: One responsibility per component
- **Props over context**: Pass data as props when possible
- **Separate 3D and UI**: Keep 3D in `Scene3D`, UI in separate components
- **Types**: Consider adding TypeScript for better DX

---

## Common Issues

### Issue: Component not updating
**Solution**: Check if you're mutating state instead of creating new objects
```jsx
// ❌ Wrong
agents[0].status = 'processing'  // Mutation

// ✅ Correct
setAgents(prev => prev.map(a => 
  a.id === id ? { ...a, status: 'processing' } : a
))
```

### Issue: useFrame callback not running
**Solution**: Ensure component is inside `<Canvas>` and ref is attached
```jsx
function MyComponent() {
  const ref = useRef()
  useFrame(() => {
    if (ref.current) {  // Check ref exists
      ref.current.rotation.y += 0.01
    }
  })
  return <mesh ref={ref}>...</mesh>
}
```

### Issue: Objects not visible
**Solutions**:
- Check camera position relative to objects
- Ensure lighting is adequate
- Check material properties (not using MeshBasicMaterial without lights)
- Verify scale isn't too small or too large

### Issue: Performance drops
**Solutions**:
- Reduce geometry complexity (fewer vertices)
- Use instancing for repeated objects
- Disable shadows if not needed
- Reduce post-processing quality
- Check for memory leaks (disposals)

---

## Feature Ideas

Refer to R3F_REFERENCE.md → [Next Steps for AG-Organism](#next-steps-for-ag-organism)

### Quick Wins
- ✅ Add Stars background
- ✅ Add Grid helper
- ✅ Environment preset lighting
- ✅ Spring animations for selection

### Medium Effort
- Particle trails between agents
- Custom shaders for auras
- Click agents in 3D to select
- Data flow visualization

### Complex
- GLTF model loading
- Physics simulation
- VR support
- Real-time collaboration

---

## Testing Checklist

Before committing changes:

- [ ] Runs in dev mode (`npm run dev`)
- [ ] Builds without errors (`npm run build`)
- [ ] Serves correctly (`npm run serve`)
- [ ] Docker builds successfully
- [ ] No console errors in browser
- [ ] Maintains 60fps (check browser DevTools Performance tab)
- [ ] Mobile responsive (test in DevTools device mode)
- [ ] API integration works (if modified)
- [ ] All existing features still work

---

## Deployment

Changes deploy automatically via GitHub Actions when merged to main.

Manual deployment:
```bash
# From repository root
cd infrastructure/terraform
terraform plan -target=google_cloud_run_v2_service.ag_organism_frontend
terraform apply -target=google_cloud_run_v2_service.ag_organism_frontend
```

---

## Resources

### Project-Specific
- **R3F Reference**: `R3F_REFERENCE.md` (detailed examples)
- **Migration Guide**: `MIGRATION.md` (architecture decisions)
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`

### External
- **R3F Docs**: https://r3f.docs.pmnd.rs/
- **R3F Examples**: https://r3f.docs.pmnd.rs/getting-started/examples
- **Drei Helpers**: https://github.com/pmndrs/drei
- **Post-Processing**: https://github.com/pmndrs/react-postprocessing
- **Three.js Docs**: https://threejs.org/docs/

---

## Getting Help

1. **Check R3F_REFERENCE.md** for examples
2. **Search R3F docs**: https://r3f.docs.pmnd.rs/
3. **Check issues**: https://github.com/pmndrs/react-three-fiber/issues
4. **Discord**: https://discord.gg/poimandres (Poimandres community)

---

**Last Updated**: 2025-12-06  
**Current Version**: React 18.2.0, R3F 8.15.16, Drei 9.96.1
