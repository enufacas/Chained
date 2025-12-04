# Visual Shape Guide for Organism.html

This guide shows the visual representation of each agent type in the 3D visualization.

## Agent Shape Legend

### Organization & Structure
```
organize-guru: ⬜ BOX
- Geometric: Cube/Box
- Symbolizes: Structure, organization, SOLID principles
- Color: Cyan (#00ffff)
- Example: Robert Martin
```

### Testing & Quality
```
assert-specialist: ⬡ OCTAHEDRON
- Geometric: 8-sided polyhedron
- Symbolizes: Multi-faceted testing, all angles covered
- Color: Green (#00ff00)
- Example: Tesla (assert)
```

### Security & Protection
```
secure-specialist: ▲ CONE
- Geometric: Pointed cone
- Symbolizes: Vigilance, pointed defense, always alert
- Color: Red (#ff0000)
- Example: Security agents
```

### Performance & Speed
```
accelerate-master: ⭕ TORUS
- Geometric: Donut/Ring
- Symbolizes: Continuous flow, optimization loops
- Color: Yellow (#ffff00)
- Example: Performance specialists
```

### Creation & Innovation
```
create-botter: ⬢ DODECAHEDRON
- Geometric: 12-sided polyhedron
- Symbolizes: Complexity, creative solutions
- Color: Magenta (#ff00ff)
- Example: Infrastructure creators
```

### Analysis & Investigation
```
investigate-champion: ⬟ ICOSAHEDRON
- Geometric: 20-sided polyhedron
- Symbolizes: Many perspectives, thorough analysis
- Color: Purple (#9900ff)
- Example: Code investigators
```

### Integration & Connection
```
bridge-master: ⬤ CYLINDER
- Geometric: Cylindrical pillar
- Symbolizes: Connecting, bridging systems
- Color: Teal (#00ffaa)
- Example: Integration specialists
```

### Documentation & Clarity
```
document-ninja: ◻ PLANE
- Geometric: Flat plane
- Symbolizes: Clear, flat documentation, easy to read
- Color: White (#ffffff)
- Example: Documentation agents
```

### Coaching & Teaching
```
coach-master: ▼ TETRAHEDRON
- Geometric: 4-sided pyramid
- Symbolizes: Foundation, building from basics
- Color: Orange (#ff9900)
- Example: Code reviewers, mentors
```

### CI/CD & Workflow
```
align-wizard: 💊 CAPSULE
- Geometric: Pill-shaped capsule
- Symbolizes: Streamlined, efficient pipelines
- Color: Light Blue (#00aaff)
- Example: CI/CD specialists
```

### Pioneering & Exploration
```
pioneer-sage: ⭐ STAR (5-pointed)
- Geometric: Extruded star shape
- Symbolizes: Shining innovation, leading the way
- Color: Pink (#ff0099)
- Example: New technology explorers
```

### Development (General)
```
develop-specialist: ● SPHERE
- Geometric: Perfect sphere
- Symbolizes: Well-rounded, general development
- Color: Violet (#aa00ff)
- Example: General developers
```

### Engineering
```
engineer-master: ⬜ BOX
- Geometric: Structured box
- Symbolizes: Systematic, engineering precision
- Color: Deep Orange (#ff6600)
- Example: API engineers
```

### Infrastructure
```
infrastructure-specialist: ⬤ CYLINDER
- Geometric: Support column
- Symbolizes: Foundation, supporting systems
- Color: Blue (#0066ff)
- Example: Infrastructure builders
```

### Tools & Utilities
```
tools-analyst: ⭕ TORUS
- Geometric: Ring/Torus
- Symbolizes: Utility, continuous improvement
- Color: Lime (#66ff00)
- Example: Tool developers
```

## Size Variations

Agents are sized based on their overall performance score:

```
Small:  0.5 units (score < 0.3)
Medium: 1.0 units (score 0.3-0.7)
Large:  2.0 units (score > 0.7)
```

## Status Indicators

### Emissive Glow
- **Working agents**: Brighter glow, pulsing (0.3-0.6 intensity)
- **Exploring agents**: Dimmer glow, steady (0.2 intensity)

### Distance from Core
- **Working**: 25 units (inner ring)
- **Exploring**: 35 units (outer ring)

### Connections
- **Working agents**: Connected to core with glowing line
- **Exploring agents**: No connection line

## Mission Objects

```
Complete Mission: ⬢ Green Octahedron
- Color: #00ff00
- Size: 0.3 units
- Rotation: Slow spinning

In-Progress Mission: ⬢ Orange Octahedron
- Color: #ffaa00
- Size: 0.3 units
- Rotation: Faster spinning
```

Positioned in outer ring at 45 units distance.

## Label Display

```
┌─────────────────┐
│  Agent Name     │ ← CSS3D label
└─────────────────┘
        │
        ↓
    [Shape] ← 3D geometry
        │
        ↓ (floating animation)
```

Labels:
- Positioned 3 units above agent
- Follow agent during floating animation
- Scale: 0.05x
- Style: Cyan text, semi-transparent background

## Color Meanings

| Color | Specialization | Hex |
|-------|----------------|-----|
| Cyan | Organization | #00ffff |
| Green | Testing | #00ff00 |
| Red | Security | #ff0000 |
| Yellow | Performance | #ffff00 |
| Magenta | Creation | #ff00ff |
| Purple | Investigation | #9900ff |
| Teal | Integration | #00ffaa |
| White | Documentation | #ffffff |
| Orange | Coaching | #ff9900 |
| Light Blue | CI/CD | #00aaff |
| Pink | Innovation | #ff0099 |
| Violet | Development | #aa00ff |
| Deep Orange | Engineering | #ff6600 |
| Blue | Infrastructure | #0066ff |
| Lime | Tools | #66ff00 |

## Scene Layout

```
                    Mission Objects (45 units)
                  ⬢ ⬢ ⬢ ⬢ ⬢ ⬢ ⬢ ⬢ ⬢ ⬢
                 ╱                       ╲
                ╱   Exploring Agents      ╲
               ⬢ ⬡ ▲ ⬜ ⬤ (35 units) ⭐ ⬢ ⬡
              ╱                             ╲
             ╱     Working Agents (25 units) ╲
            ⬜ ⬡ ▲ ⭕ ⬢ ⬟ ⬤ ◻ ▼ 💊 ⭐
           ╱                                 ╲
          ╱        Lifecycle Core (0,0,0)    ╲
         ●━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━●
          ╲        Connection Lines         ╱
           ╲    (only for working agents)  ╱
            ╲                             ╱
```

## Interaction Guide

### Mouse Controls
- **Left Click + Drag**: Rotate view
- **Right Click + Drag**: Pan view
- **Scroll Wheel**: Zoom in/out
- **Click Agent**: Select and show details

### Sidebar Controls
- **Click Agent Name**: Focus camera on agent in 3D
- **Scroll List**: Browse all agents
- **Filter (if implemented)**: Show specific types

### Keyboard Shortcuts (potential)
- **R**: Reset camera view
- **P**: Toggle particles
- **C**: Toggle connections
- **L**: Toggle labels
- **+/-**: Adjust animation speed

## Visualization at a Glance

When viewing the organism.html page, you'll see:

1. **Center**: Glowing lifecycle core
2. **Inner Ring (25u)**: Working agents with unique shapes, labels, and connections
3. **Outer Ring (35u)**: Exploring agents with unique shapes and labels
4. **Far Ring (45u)**: Mission objects (green/orange octahedrons)
5. **Background**: Particle system (stars/dust)
6. **Sidebar Left**: Agent list with click-to-focus
7. **Sidebar Right**: System statistics

## Tips for Best Viewing

1. **Initial Load**: Wait for data to load (2-3 seconds)
2. **Camera Position**: Start at (0, 25, 50) for overview
3. **Agent Details**: Click agents for full information
4. **Performance**: Disable particles if laggy
5. **Exploration**: Rotate and zoom to see all angles
6. **Mission Discovery**: Zoom out to see mission ring

---

This visual guide helps understand the shape-to-role mapping at a glance!
