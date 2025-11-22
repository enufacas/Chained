---
applyTo:
  - "docs/organism.html"
  - "docs/lifecycle-3d.html"
  - "docs/**/*3d*.html"
  - "docs/**/*three*.html"
  - "docs/**/*.html" # When containing Three.js code
---

# 3D Web Rendering with Three.js - Requirements and Best Practices

## MANDATORY RULE: Test 3D Rendering Performance and Visual Quality

When working with Three.js visualizations in the `docs/` directory, **you MUST test rendering performance, visual quality, and cross-device compatibility** before completing your task.

## Why This Matters

3D web rendering is performance-critical and visually impactful. Poor performance or visual issues directly affect user experience and project perception. Testing ensures:

1. **Performance**: 60fps target on mid-range devices
2. **Visual Quality**: Effects render as intended without artifacts
3. **Mobile Support**: Works on mobile devices with touch controls
4. **Memory Management**: No memory leaks from Three.js objects
5. **Browser Compatibility**: Works across Chrome, Firefox, Safari
6. **User Experience**: Smooth interactions and intuitive controls

## When to Test

You MUST test 3D rendering in these scenarios:

### Always Required
- ✅ Modifying Three.js scene setup or render loop
- ✅ Adding/changing geometries, materials, or lights
- ✅ Implementing particle systems or instanced rendering
- ✅ Adding post-processing effects (bloom, SSAO, etc.)
- ✅ Changing camera controls or animation systems
- ✅ Optimizing draw calls or GPU performance
- ✅ Adding touch controls or mobile optimizations

### Conditionally Required
- 🔄 Changes to data loading that affect 3D objects
- 🔄 UI controls that interact with the 3D scene
- 🔄 CSS changes that might affect canvas sizing

## Performance Requirements

### Target Specifications
- **Frame Rate**: 60fps on mid-range desktop (i5/Ryzen 5 + integrated graphics)
- **Mobile Frame Rate**: 30-60fps on mid-range mobile (2-year-old devices)
- **Draw Calls**: < 50 per frame (prefer < 20)
- **Memory Usage**: < 200MB total (including textures)
- **Load Time**: < 3 seconds for scene initialization
- **GPU Usage**: < 80% on target hardware

### Performance Testing Checklist
- [ ] Check FPS using browser DevTools Performance tab
- [ ] Monitor draw calls in Three.js renderer stats
- [ ] Test memory usage and check for leaks
- [ ] Profile on both desktop and mobile devices
- [ ] Verify GPU usage doesn't throttle CPU
- [ ] Test with browser throttling enabled (3G network, 4x CPU slowdown)

## Visual Quality Requirements

### Visual Testing Checklist
- [ ] Bloom/glow effects don't bleed excessively
- [ ] Colors match design specifications
- [ ] Lighting creates appropriate atmosphere
- [ ] Particles/effects animate smoothly
- [ ] Shadows render correctly (if used)
- [ ] No z-fighting or rendering artifacts
- [ ] Text/labels are readable and properly positioned
- [ ] Camera movements are smooth and intuitive

### Screenshot Requirements
**CRITICAL**: When making visual changes to 3D scenes:

1. **Take BEFORE screenshot** (if modifying existing scene)
2. **Take AFTER screenshot** (showing your changes)
3. **Take PERFORMANCE screenshot** (showing FPS/draw calls/memory)
4. **Include screenshots in PR description**

Use Playwright's `browser_take_screenshot` tool after navigating to the page.

## Testing Methods

### Method 1: Local HTTP Server + Browser DevTools

```bash
# Start local server
cd docs
python3 -m http.server 8000

# Then open in browser:
# http://localhost:8000/organism.html
# http://localhost:8000/lifecycle-3d.html
```

**DevTools Performance Checks:**
1. Open DevTools (F12)
2. Go to Performance tab
3. Start recording
4. Interact with 3D scene for 10 seconds
5. Stop recording
6. Check:
   - FPS should be near 60
   - No long tasks (> 50ms)
   - GPU usage reasonable
   - No excessive garbage collection

### Method 2: Three.js Stats Panel

Add Stats.js to your scene for real-time monitoring:

```javascript
import Stats from 'three/addons/libs/stats.module.js';

const stats = new Stats();
document.body.appendChild(stats.dom);

function animate() {
    stats.begin();
    // ... your render code
    stats.end();
}
```

Monitor:
- **FPS**: Target 60, minimum 30
- **MS**: Frame time < 16ms for 60fps
- **MB**: Memory usage should be stable

### Method 3: Playwright Browser Automation

Use Playwright for automated testing and screenshots:

```markdown
# Navigate to 3D page
@playwright-browser_navigate url="http://localhost:8000/organism.html"

# Wait for Three.js to initialize
@playwright-browser_wait_for time=2

# Take screenshot of 3D scene
@playwright-browser_take_screenshot filename="organism-3d-scene.png"

# Check console for errors
@playwright-browser_console_messages

# Test performance
@playwright-browser_evaluate function="() => {
    return {
        fps: window.performance.now(),
        memory: performance.memory.usedJSHeapSize
    };
}"
```

### Method 4: Mobile Device Testing

Test on actual mobile devices or emulation:

```markdown
# Resize browser to mobile viewport
@playwright-browser_resize width=375 height=667

# Test touch interactions
@playwright-browser_click element="canvas"

# Take mobile screenshot
@playwright-browser_take_screenshot filename="organism-mobile.png"
```

## Three.js Best Practices

### Geometry Optimization
```javascript
// ✅ GOOD: Reuse geometry
const geometry = new THREE.SphereGeometry(1, 32, 32);
for (let i = 0; i < 100; i++) {
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
}

// ❌ BAD: Create new geometry for each object
for (let i = 0; i < 100; i++) {
    const geometry = new THREE.SphereGeometry(1, 32, 32);
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
}
```

### Material Optimization
```javascript
// ✅ GOOD: Reuse materials
const material = new THREE.MeshStandardMaterial({ color: 0x00ffff });

// ❌ BAD: Clone materials unnecessarily
const material = baseMaterial.clone();
```

### Instanced Rendering for Many Objects
```javascript
// ✅ GOOD: Use InstancedMesh for 100+ similar objects
const geometry = new THREE.SphereGeometry(1, 32, 32);
const material = new THREE.MeshStandardMaterial({ color: 0x00ffff });
const instancedMesh = new THREE.InstancedMesh(geometry, material, 200);

for (let i = 0; i < 200; i++) {
    const matrix = new THREE.Matrix4();
    matrix.setPosition(x, y, z);
    instancedMesh.setMatrixAt(i, matrix);
}

// ❌ BAD: Individual meshes for particles
for (let i = 0; i < 200; i++) {
    const mesh = new THREE.Mesh(geometry, material);
    scene.add(mesh);
}
```

### Proper Cleanup
```javascript
// ✅ GOOD: Dispose of Three.js objects
function cleanup() {
    geometry.dispose();
    material.dispose();
    texture.dispose();
    renderer.dispose();
    
    // Remove from scene
    scene.remove(mesh);
}

// ❌ BAD: Memory leaks
// Just removing from scene without disposal
scene.remove(mesh);
```

### Efficient Render Loop
```javascript
// ✅ GOOD: Only render when needed
let needsRender = true;

function animate() {
    requestAnimationFrame(animate);
    
    controls.update();
    
    if (needsRender) {
        renderer.render(scene, camera);
        needsRender = false;
    }
}

controls.addEventListener('change', () => {
    needsRender = true;
});
```

## organism.html Specific Guidelines

### Current Implementation
- Uses Three.js r160 with ES6 modules via CDN
- Implements OrbitControls for camera manipulation
- Uses CSS3DRenderer for HTML label overlay
- Post-processing with EffectComposer, UnrealBloomPass
- Particle system for data flow visualization

### Performance Optimization Opportunities
1. **Use InstancedMesh for agent spheres** (47 agents → 1 draw call)
2. **Use InstancedMesh for particles** (200 particles → 1 draw call)
3. **Reduce particle count on mobile** (200 → 100 or fewer)
4. **Use LOD for distant objects** (simplified geometry when far)
5. **Frustum culling** (don't render off-screen objects)
6. **Texture atlases** (combine textures to reduce draw calls)

### Visual Enhancement Opportunities
1. **Better bloom intensity** (adjust threshold and strength)
2. **Particle trails** (using BufferGeometry with positions)
3. **Smooth color transitions** (lerp between colors on hover)
4. **Camera tours** (tween.js for smooth animations)
5. **Agent selection highlight** (OutlinePass for selected agent)
6. **Depth of field** (BokehPass for focus effects)

### Mobile Optimization Guidelines
```javascript
// Detect mobile and adjust quality
const isMobile = /Android|iPhone|iPad/i.test(navigator.userAgent);

if (isMobile) {
    // Reduce particle count
    particleCount = 100;
    
    // Simplify geometry
    sphereSegments = 16; // instead of 32
    
    // Disable expensive effects
    bloomPass.enabled = false;
    
    // Lower resolution
    renderer.setPixelRatio(1); // instead of window.devicePixelRatio
}
```

## Common Issues and Solutions

### Issue: Low FPS
**Causes:**
- Too many draw calls (check renderer.info.render.calls)
- Too many vertices (check renderer.info.render.triangles)
- Expensive post-processing effects
- Unoptimized particle systems

**Solutions:**
- Use InstancedMesh for repeated objects
- Reduce geometry complexity (lower segment count)
- Disable bloom on mobile
- Batch similar objects with same material

### Issue: Memory Leaks
**Causes:**
- Not disposing geometries, materials, textures
- Adding listeners without removing
- Holding references to disposed objects

**Solutions:**
- Call dispose() on all Three.js objects
- Remove event listeners on cleanup
- Set references to null after disposal

### Issue: Jerky Camera Movement
**Causes:**
- Not using damping on OrbitControls
- Frame rate drops during movement
- Large camera position changes

**Solutions:**
- Enable damping: `controls.enableDamping = true;`
- Use tween.js for smooth transitions
- Limit camera rotation speed

### Issue: Text Labels Overlap
**Causes:**
- Static label positioning
- Too many visible labels
- No collision detection

**Solutions:**
- Implement label hiding when overlapping
- Use CSS3DRenderer for HTML labels
- Show labels only on hover
- Implement smart label positioning algorithm

## Documentation Requirements

When documenting 3D rendering work:

### In Code Comments
```javascript
// Performance: Using InstancedMesh for 200 particles (1 draw call)
// Instead of 200 individual meshes (200 draw calls)
const instancedMesh = new THREE.InstancedMesh(geometry, material, 200);
```

### In PR Description
```markdown
## Performance Metrics

**Before:**
- FPS: 45 (desktop), 20 (mobile)
- Draw Calls: 250
- Memory: 300MB

**After:**
- FPS: 60 (desktop), 50 (mobile)
- Draw Calls: 15
- Memory: 150MB

**Screenshots:**
- [Before Performance](link)
- [After Performance](link)
- [Visual Comparison](link)
```

### In Commit Messages
```
perf: optimize agent sphere rendering with InstancedMesh

Reduced draw calls from 47 to 1 by using InstancedMesh.
Frame rate improved from 45fps to 60fps on test devices.
Memory usage reduced by 50MB.

Screenshots show performance improvement in DevTools.
```

## Browser Compatibility

### Minimum Requirements
- **WebGL 1.0** support (check with: `renderer.capabilities.isWebGL2`)
- **ES6 modules** support
- **requestAnimationFrame** support

### Feature Detection
```javascript
// Check WebGL support
if (!renderer.capabilities.isWebGL2) {
    console.warn('WebGL2 not supported, using WebGL1');
    // Disable advanced features
}

// Check mobile
const isMobile = /Android|iPhone|iPad/i.test(navigator.userAgent);
```

### Fallback Strategy
```javascript
// If WebGL not supported
if (!window.WebGLRenderingContext) {
    document.getElementById('canvas-container').innerHTML = 
        '<div class="fallback">Your browser does not support 3D graphics. Please use a modern browser.</div>';
    return;
}
```

## Accessibility Considerations

### Keyboard Controls
```javascript
// Implement keyboard navigation
document.addEventListener('keydown', (e) => {
    switch(e.key) {
        case 'ArrowUp':
            camera.position.y += 1;
            break;
        case 'ArrowDown':
            camera.position.y -= 1;
            break;
        // ... more controls
    }
});
```

### Screen Reader Support
```html
<!-- Add ARIA labels to canvas -->
<canvas id="canvas" 
        role="img" 
        aria-label="3D visualization of the autonomous AI ecosystem">
</canvas>

<!-- Provide text alternative -->
<div class="sr-only">
    Interactive 3D visualization showing 47 AI agents...
</div>
```

### Motion Reduction
```javascript
// Respect prefers-reduced-motion
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (prefersReducedMotion) {
    // Disable or reduce animations
    controls.autoRotate = false;
    particleSpeed = 0.1; // slower
}
```

## Summary Checklist

Before completing 3D rendering work:

- [ ] Test on local server (python3 -m http.server 8000)
- [ ] Check FPS is 60 on desktop, 30+ on mobile
- [ ] Verify draw calls are < 50 (ideally < 20)
- [ ] Monitor memory usage (no leaks)
- [ ] Test on mobile viewport (Playwright resize)
- [ ] Take before/after screenshots
- [ ] Capture performance metrics screenshot
- [ ] Check browser console for errors
- [ ] Verify visual quality (bloom, colors, lighting)
- [ ] Test camera controls (mouse, touch, keyboard)
- [ ] Ensure proper cleanup and disposal
- [ ] Document performance improvements in PR
- [ ] Test on actual mobile device if possible

---

*🎨 3D rendering guidelines for the render-3d-master agent and all Three.js work. Performance and visual quality are paramount.*
