# AG-Organism Factory Theme Guide

## Overview

The AG-Organism has been redesigned with a **futuristic factory** aesthetic, moving away from the cyberpunk neon theme to an industrial, manufacturing-floor inspired visual style.

## Visual Concept

The factory theme represents an **autonomous AI agent assembly line**, where agents work together like specialized machines in a modern smart factory.

### Key Visual Elements

1. **Factory Platform** - Central assembly area where agents operate
2. **Orbital Rings** - Data transfer paths and energy flows
3. **Industrial Pillars** - Factory support infrastructure
4. **Grid Floor** - Manufacturing floor grid system
5. **Data Streams** - Information flow visualization
6. **Factory Lighting** - Industrial overhead and accent lighting

---

## Color Palette

### Primary Colors

| Use | Color | Hex | RGB |
|-----|-------|-----|-----|
| Background | Dark Industrial | `#0d1117` | rgb(13, 17, 23) |
| Surface | Dark Surface | `#161b22` | rgb(22, 27, 34) |
| Primary Blue | Factory Blue | `#4a9eff` | rgb(74, 158, 255) |
| Text Primary | Light | `#e6edf3` | rgb(230, 237, 243) |
| Text Secondary | Muted | `#8b949e` | rgb(139, 148, 158) |

### Agent Colors (Modern Palette)

| Agent | Color | Hex |
|-------|-------|-----|
| Academic Research | Blue | `#60a5fa` |
| Google Trends | Indigo | `#818cf8` |
| Blog Writer | Emerald | `#34d399` |
| Code Reviewer | Violet | `#a78bfa` |
| Data Analyst | Sky Blue | `#38bdf8` |
| Image Generator | Pink | `#f472b6` |

### Status Colors

| Status | Color | Hex |
|--------|-------|-----|
| Idle | Gray | `#6b7280` |
| Processing | Amber | `#fbbf24` |
| Completed | Green | `#4ade80` |
| Failed | Red | `#ef4444` |

### Accent Colors

| Use | Color | Hex |
|-----|-------|-----|
| Light Blue | Sky | `#6dd5ff` |
| Lighter Blue | Cyan | `#8fe3ff` |
| Platform | Steel | `#2a3142` |
| Grid Main | Navy | `#2a4d6e` |
| Grid Section | Ocean | `#3a6d9e` |

---

## 3D Scene Components

### 1. Factory Platform

**File:** `src/components/Scene3D.jsx` (FactoryPlatform component)

**Description:** Central cylindrical platform where agents are positioned.

**Features:**
- Metallic material (#2a3142)
- High metalness (0.8) and low roughness (0.3)
- Glowing blue edge ring (#4a9eff)
- Positioned at y: -2

**Geometry:**
- Main: CylinderGeometry (radius: 25-26, height: 1)
- Edge: TorusGeometry (radius: 25, tube: 0.3)

### 2. Factory Rings

**File:** `src/components/Scene3D.jsx` (FactoryRings component)

**Description:** Three rotating orbital rings representing data transfer paths.

**Features:**
- **Outer Ring** - Rotates at 0.1 rad/frame, horizontal
  - Radius: 30, tube: 0.2
  - Color: #4a9eff
  - Opacity: 0.6
  
- **Middle Ring** - Rotates at -0.15 rad/frame, tilted π/4
  - Radius: 22, tube: 0.15
  - Color: #6dd5ff
  - Opacity: 0.5
  - Position: y: 5
  
- **Inner Ring** - Rotates at 0.08 rad/frame, tilted -π/6
  - Radius: 28, tube: 0.18
  - Color: #8fe3ff
  - Opacity: 0.4
  - Position: y: -5

### 3. Factory Pillars

**File:** `src/components/Scene3D.jsx` (FactoryPillars component)

**Description:** Four support pillars positioned at cardinal directions.

**Positions:** [30, 0, 0], [-30, 0, 0], [0, 0, 30], [0, 0, -30]

**Features:**
- Box geometry (1.5 x 20 x 1.5)
- Steel material (#353d52)
- Point light at top (y: 10, color: #4a9eff)
- Glowing indicator sphere (radius: 0.5)

### 4. Data Streams

**File:** `src/components/Scene3D.jsx` (DataStreams component)

**Description:** 50 animated particles representing data flow.

**Features:**
- Particles orbit in circular paths
- Vertical floating animation
- Blue color gradient (RGB: 0.3-0.6, 0.6-1.0, 1.0)
- Additive blending for glow effect
- Size: 0.3 with size attenuation

**Animation:**
- Circular rotation at 0.1 rad/s
- Vertical sine wave (amplitude: 5)
- Individual phase offsets

### 5. Grid Floor

**File:** `src/components/Scene3D.jsx`

**Features:**
- Size: 100x100 units
- Cell size: 2 units
- Section size: 10 units (every 5 cells)
- Cell color: #2a4d6e
- Section color: #3a6d9e
- Fade distance: 80 units
- Position: y: -2.5

---

## Lighting Setup

### Ambient Light
- Intensity: 0.4
- Color: #b8d4ff (cool blue-white)

### Directional Light (Main)
- Position: [30, 50, 20]
- Intensity: 1.2
- Color: White
- Casts shadows

### Spotlight
- Position: [0, 40, 0]
- Angle: π/3
- Penumbra: 0.5
- Color: #6dd5ff

### Point Light (Overhead)
- Position: [0, 30, 0]
- Color: #4a9eff
- Intensity: 2
- Distance: 80

### Pillar Lights (4x)
- Position: At each pillar top
- Color: #4a9eff
- Intensity: 1
- Distance: 20

---

## UI Theme

### Header
- Background: Linear gradient #161b22 → #21262d
- Border: 2px solid #4a9eff
- Shadow: Blue glow (rgba(74, 158, 255, 0.2))
- Text: #e6edf3
- Status text: #60a5fa

### Panels (Agent Panel, Prompt Panel)
- Background: rgba(22, 27, 34, 0.95)
- Border: 2px solid #4a9eff
- Text primary: #e6edf3
- Text secondary: #8b949e
- Accent: #4a9eff

### Buttons
- Border: 1px solid #4a9eff
- Background: Transparent → rgba(74, 158, 255, 0.15) on hover
- Color: #4a9eff → #60a5fa on hover
- Border radius: 6px
- Font weight: 500

### Agent Cards
- Background: rgba(74, 158, 255, 0.05)
- Border-left: 3px solid #4a9eff
- Hover: rgba(74, 158, 255, 0.15)
- Selected: rgba(129, 140, 248, 0.2) with #818cf8 border

### Scrollbars
- Track: rgba(13, 17, 23, 0.5)
- Thumb: rgba(74, 158, 255, 0.5)
- Thumb hover: rgba(74, 158, 255, 0.8)
- Width: 8px

---

## Agent Humanoids

### Materials
- Metalness: 0.9
- Roughness: 0.1
- Emissive intensity: 0.6 (idle), 0.8 (processing)

### Color Assignment
Defined in `src/components/AgentHumanoid.jsx`:
```javascript
const colors = {
  'academic-research': 0x60a5fa,   // Blue
  'google-trends': 0x818cf8,       // Indigo
  'blog-writer': 0x34d399,         // Emerald
  'code-reviewer': 0xa78bfa,       // Violet
  'data-analyst': 0x38bdf8,        // Sky blue
  'image-generator': 0xf472b6,     // Pink
};
```

### Status Colors
- Idle: Agent-specific color
- Processing: #fbbf24 (amber)
- Completed: #4ade80 (green)
- Failed: #ef4444 (red)

---

## Animation Details

### Agent Floating
- Frequency: 2 rad/s
- Amplitude: 1 unit
- Phase offset: Random per agent

### Ring Rotation
- Outer: 0.1 rad/frame (clockwise)
- Middle: -0.15 rad/frame (counter-clockwise)
- Inner: 0.08 rad/frame (clockwise)

### Data Streams
- Orbital speed: 0.1 rad/s
- Vertical frequency: 0.5 rad/s
- Vertical amplitude: 5 units

### Agent Processing State
- Rotation: 0.02 rad/frame on Y axis
- Emissive boost: 0.6 → 0.8

---

## Design Philosophy

### Industrial Aesthetics
- **Clean lines** - Geometric precision
- **Metallic materials** - High metalness, low roughness
- **Blue monochrome** - Industrial blue palette with subtle variations
- **Functional design** - Every element serves a purpose
- **Modern manufacturing** - Smart factory, automation theme

### Color Theory
- **Primary blue** (#4a9eff) - Trust, technology, precision
- **Cool tones** - Professional, industrial atmosphere
- **High contrast** - Readability and visual hierarchy
- **Glow effects** - Energy, activity, data flow

### Spatial Design
- **Central platform** - Focus point, work area
- **Orbital rings** - Flow, circulation, connectivity
- **Vertical pillars** - Support, structure, boundaries
- **Grid floor** - Order, measurement, precision

---

## Customization Guide

### Changing Colors

**Primary blue:**
```javascript
// Update in multiple files
#4a9eff → your_new_color
```

**Files to update:**
- `src/index.css` - Scrollbars
- `src/components/Header.css` - Header border/buttons
- `src/components/AgentPanel.css` - Panel borders/accents
- `src/components/PromptPanel.css` - Panel borders/accents
- `src/components/ControlPanel.css` - Button borders
- `src/components/Scene3D.jsx` - Ring colors, lights, grid

### Adding New 3D Elements

1. Create component in Scene3D.jsx
2. Use factory color palette
3. Add subtle animation (if appropriate)
4. Ensure metallic materials (metalness: 0.8+)
5. Consider emissive properties for glow

**Example:**
```jsx
function FactoryElement() {
  return (
    <mesh>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial 
        color="#4a9eff"
        metalness={0.9}
        roughness={0.1}
        emissive="#4a9eff"
        emissiveIntensity={0.3}
      />
    </mesh>
  );
}
```

### Adjusting Lighting

**Brighter factory:**
- Increase ambientLight intensity (0.4 → 0.6)
- Increase directionalLight intensity (1.2 → 1.5)

**Darker factory:**
- Decrease ambientLight intensity (0.4 → 0.2)
- Reduce pointLight distance (80 → 50)

**Different color temperature:**
- Warm: Change ambientLight color to #ffd4b8
- Cool: Keep current #b8d4ff
- Neutral: Change to #ffffff

---

## Performance Considerations

### Optimizations Applied
- Geometry reuse via useMemo
- Material reuse where possible
- Limited particle count (50)
- No external texture loading
- Efficient animation loops

### Frame Rate Targets
- Desktop: 60fps
- Mobile: 30-60fps
- Tablet: 45-60fps

### Memory Usage
- Typical: < 200MB
- Peak: < 300MB

---

## References

For implementation details and R3F patterns:
- **R3F_REFERENCE.md** - Comprehensive React Three Fiber guide
- **ITERATION_GUIDE.md** - Development workflow
- **IMPLEMENTATION_SUMMARY.md** - Technical architecture

For examples and inspiration:
- https://r3f.docs.pmnd.rs/getting-started/examples
- https://github.com/pmndrs/react-three-fiber
- https://github.com/pmndrs/drei

---

## Version History

- **v2.0.0** (2025-12-06) - Factory theme implementation with R3F migration
- Repository: `/home/runner/work/Chained/Chained/infrastructure/docker/ag-organism-frontend/`
