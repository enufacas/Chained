---
applyTo:
  - "docs/organism.html"
  - "docs/lifecycle-3d.html"
  - "docs/**/*3d*.html"
  - "docs/**/*three*.html"
---

# 3D Web Rendering with Three.js - Quick Reference

## MANDATORY: Test 3D Rendering Performance

When working with Three.js visualizations, **you MUST test rendering performance and visual quality** before completing your task.

### Performance Targets
- **Frame Rate**: 60fps on desktop, 30-60fps on mobile
- **Draw Calls**: < 50 per frame (prefer < 20)
- **Memory**: < 200MB total

### Testing Steps
1. Start local server: `cd docs && python3 -m http.server 8000`
2. Open in browser and check DevTools Performance tab
3. Monitor FPS, draw calls, and memory usage
4. Test on mobile viewport
5. Take screenshots: before, after, performance metrics

### Key Optimizations
- Use `InstancedMesh` for repeated objects (reduces draw calls)
- Reuse geometries and materials
- Dispose of Three.js objects properly to prevent memory leaks
- Reduce particle count on mobile devices
- Use LOD (Level of Detail) for distant objects

### Playwright Testing
```javascript
// Navigate and test
browser_navigate url="http://localhost:8000/organism.html"
browser_wait_for time=2
browser_take_screenshot filename="3d-scene.png"
browser_console_messages  // Check for errors
```

**For detailed guidance**, see: [docs/guides/copilot-instructions/threejs-rendering-guide.md](../../../docs/guides/copilot-instructions/threejs-rendering-guide.md)
