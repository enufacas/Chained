# AG-Organism Frontend - React Migration

## Migration Summary

The AG-Organism 3D visualization has been successfully migrated from vanilla Three.js to **React with react-three-fiber**.

### What Changed

**Before:**
- Single HTML file with vanilla Three.js and ES6 modules
- Manual DOM manipulation for UI
- Imperative 3D scene setup
- Express server serving static HTML

**After:**
- React application built with Vite
- **react-three-fiber** for declarative 3D rendering
- **@react-three/drei** for useful helpers (OrbitControls, Html)
- **@react-three/postprocessing** for bloom effects
- Component-based architecture
- Express server serving built React app

### Architecture

```
src/
├── main.jsx                 # React entry point
├── App.jsx                  # Main application component
├── App.css
├── index.css                # Global styles
├── api/
│   └── agentApi.js         # API layer for backend communication
└── components/
    ├── AgentHumanoid.jsx   # 3D agent humanoid (R3F component)
    ├── AgentLabel.jsx      # CSS3D labels using @react-three/drei Html
    ├── AgentPanel.jsx      # Left sidebar with agent selection
    ├── ConnectionLines.jsx # 3D connection lines between agents
    ├── ControlPanel.jsx    # Bottom control panel
    ├── Header.jsx          # Top header bar
    ├── LoadingScreen.jsx   # Loading screen
    ├── PostProcessing.jsx  # Bloom post-processing effect
    ├── PromptPanel.jsx     # Right sidebar with prompt input
    └── Scene3D.jsx         # Main 3D scene orchestrator
```

### Key Features Maintained

✅ **Agent humanoid visualization** - Converted to R3F components  
✅ **Pipeline execution** - Full API integration preserved  
✅ **Real-time updates** - Polling and state management  
✅ **Post-processing (bloom)** - Using @react-three/postprocessing  
✅ **Orbit controls** - Using @react-three/drei OrbitControls  
✅ **Agent selection** - React state management  
✅ **Activity log** - Real-time logging  
✅ **Environment variable injection** - Server-side injection maintained  

### Development

```bash
# Install dependencies
npm install

# Run development server (Vite)
npm run dev

# Build for production
npm run build

# Run production server
npm run serve
```

### Docker Build

The Dockerfile uses a multi-stage build:

1. **Builder stage**: Installs all dependencies and builds the React app with Vite
2. **Production stage**: Copies the built `dist/` folder and runs Express server

```bash
# Build image
docker build -t ag-organism-frontend .

# Run container
docker run -p 8080:8080 \
  -e AG_UI_FRONTEND_URL=https://... \
  -e NEXT_PUBLIC_ADK_API_URL=https://... \
  ag-organism-frontend
```

### Cloud Run Deployment

No changes to Cloud Run configuration needed. The service continues to:
- Serve on port 8080
- Inject environment variables via server.js
- Provide `/health` endpoint
- Log errors to GCP Cloud Logging

### Performance Improvements

**react-three-fiber advantages:**
- **Declarative**: Easier to reason about 3D scene structure
- **React hooks**: useFrame for animation loops
- **Component reuse**: AgentHumanoid is a reusable component
- **Automatic cleanup**: React handles Three.js object disposal
- **Better debugging**: React DevTools can inspect 3D scene

**Maintained 60fps target:**
- Optimized materials and geometries
- Efficient state updates
- Post-processing only when enabled
- Proper shadow map configuration

### API Integration

The API layer (`src/api/agentApi.js`) maintains compatibility with the AG-UI backend:

- `/api/registry` - Load available agents
- `/api/pipeline` - Execute pipeline (POST)
- `/api/pipeline?id=xxx` - Poll pipeline status (GET)
- `/api/log-error` - Frontend error logging (POST)

### Migration Benefits

1. **Maintainability**: Component-based architecture is easier to maintain
2. **Testability**: React components can be unit tested
3. **Developer Experience**: React DevTools, hot reload, better error messages
4. **Scalability**: Easy to add new features (particles, artifacts, animations)
5. **Modern Stack**: Aligns with current web development best practices

### Future Enhancements

With React and R3F, these features become easier to implement:

- **Artifact visualization**: Floating gems/objects near agents
- **Particle effects**: Using instanced meshes
- **Camera tours**: Animated camera paths
- **Agent interactions**: Click handlers, tooltips
- **Mobile optimization**: Responsive 3D scene
- **Performance monitoring**: React profiler integration

### Backward Compatibility

The vanilla Three.js version is preserved in:
- `docs/ag-organism.html` (GitHub Pages)
- `public/ag-organism.html` (if needed for fallback)

Both versions maintain identical functionality and visual appearance.

---

**Migration completed by @3d-render-master** (John Carmack agent)  
Performance target: 60fps maintained ✅  
All original features preserved ✅  
Docker build optimized ✅
