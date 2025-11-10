# AI Knowledge Graph - Visual Preview

## What the Graph Looks Like

The AI Knowledge Graph is an interactive, force-directed network visualization that displays AI-related learnings from Hacker News and TLDR Tech as interconnected nodes.

## Graph Structure

```
                    ┌─────────────┐
                    │  GPT (Topic)│◄─────┐
                    └──────┬──────┘      │
                           │             │
                           │             │
                  ┌────────▼──────────┐  │
                  │ Study on AI eval  │  │
                  │  (Story, 332pts)  │  │
                  └───────────────────┘  │
                           │             │
                           │             │
                    ┌──────▼──────┐      │
                    │AI (Topic)   │◄─────┼──────┐
                    └──────┬──────┘      │      │
                           │             │      │
                           │             │      │
                  ┌────────▼──────────┐  │      │
                  │ AI replacing jobs │  │      │
                  │  (Story, 299pts)  │  │      │
                  └───────────────────┘  │      │
                           │             │      │
                           │             │      │
                    ┌──────▼──────┐      │      │
                    │Model (Topic)│◄─────┘      │
                    └──────┬──────┘             │
                           │                    │
                           │                    │
                  ┌────────▼──────────┐         │
                  │ GPT-5 Codex Mini │         │
                  │  (Story, 129pts)  │─────────┘
                  └───────────────────┘
```

## Node Types

### Story Nodes (Circles)
- Represent individual HN/TLDR articles
- Size proportional to story score (popularity)
- Color indicates category:
  - 🔴 Red: AI/ML Core concepts
  - 🔵 Cyan: Tools & Frameworks
  - 🟢 Blue: Applications
  - 🟡 Green: Research & Theory
  - 🟠 Orange: Industry & Business

### Topic Nodes (Larger Circles)
- Represent extracted AI/ML keywords
- Size proportional to mention count
- Labels in UPPERCASE (e.g., "GPT", "AI", "NEURAL")

## Connections (Links)

- Lines between nodes show relationships
- Stories connected to their topics
- Stories connected to other stories sharing topics
- Thicker lines = stronger relationships

## Interactive Features

### Hover Effects
When you hover over a node:
- Node grows larger
- Tooltip appears with details:
  - Full story title
  - Score/popularity
  - Category
  - Source (HN/TLDR)
  - Related topics
  - Link to original article

### Click Actions
- Click story nodes: Opens article in new tab
- Click topic nodes: No action (informational)

### Drag & Drop
- Drag nodes to reposition them
- Graph dynamically adjusts connections
- Physics simulation maintains balance

### Zoom & Pan
- Scroll to zoom in/out
- Click & drag background to pan
- "Reset View" button returns to default

## Statistics Panel (Top Left)

```
┌─────────────────────┐
│ 📊 Graph Stats      │
│                     │
│ Nodes: 45           │
│ Connections: 78     │
│ Topics: 12          │
│ Last Updated: Now   │
└─────────────────────┘
```

## Controls Panel (Top Right)

```
┌─────────────────────┐
│ 🔍 Reset View       │
│ ⚡ Toggle Physics   │
│ 💾 Export Data      │
└─────────────────────┘
```

## Legend Panel (Bottom Left)

```
┌─────────────────────────┐
│ 🏷️ Legend              │
│                         │
│ 🔴 AI/ML Core          │
│ 🔵 Tools & Frameworks  │
│ 🟢 Applications        │
│ 🟡 Research & Theory   │
│ 🟠 Industry & Business │
└─────────────────────────┘
```

## Key Insights (Below Graph)

### Trending Topics
```
┌─────────────────────────┐
│ 🔥 Trending Topics      │
│                         │
│ • GPT (8 mentions)      │
│ • AI (15 mentions)      │
│ • NEURAL (5 mentions)   │
│ • MODEL (7 mentions)    │
│ • TRAINING (4 mentions) │
└─────────────────────────┘
```

### Emerging Technologies
```
┌─────────────────────────┐
│ 🚀 Emerging Tech        │
│                         │
│ • LLM (avg: 350 pts)    │
│ • TRANSFORMER (298 pts) │
│ • RAG (275 pts)         │
└─────────────────────────┘
```

### Most Connected
```
┌─────────────────────────────────────┐
│ 🔗 Most Connected                   │
│                                     │
│ • Study on AI evaluation (6 topics)│
│ • GPT-5 Codex review (5 topics)    │
│ • Neural network basics (4 topics) │
└─────────────────────────────────────┘
```

## Animation & Physics

The graph uses D3.js force simulation:
- **Charge Force**: Nodes repel each other
- **Link Force**: Connected nodes attract
- **Center Force**: Keeps graph centered
- **Collision Force**: Prevents node overlap

Physics can be toggled on/off for performance.

## Color Scheme

The visualization uses a cyberpunk-inspired dark theme:
- Background: Dark navy (#1a1a2e)
- Primary: Cyan (#00d4ff)
- Text: Light gray (#e0e0e0)
- Accents: Category-specific colors

## Responsive Design

The graph adapts to different screen sizes:
- Desktop: Full-featured interactive experience
- Tablet: Touch-optimized controls
- Mobile: Simplified view with essential features

## Performance

- Handles 50+ nodes smoothly
- 60 FPS animation
- Lazy loading of learning data
- Efficient D3.js rendering

## Example Data Flow

```
1. User visits ai-knowledge-graph.html
   ↓
2. JavaScript loads learning files from ../learnings/
   ↓
3. Filters for AI-related stories
   ↓
4. Extracts topics (GPT, AI, neural, etc.)
   ↓
5. Builds nodes array:
   - Story nodes (from learnings)
   - Topic nodes (from keywords)
   ↓
6. Builds links array:
   - Story → Topic connections
   - Story → Story connections (if shared topics)
   ↓
7. D3.js renders force-directed graph
   ↓
8. User interacts (hover, click, drag)
   ↓
9. Insights generated and displayed
```

## Real Example

Based on actual data:

**Story 1**: "Study identifies weaknesses in how AI systems are evaluated"
- Score: 332
- Topics: [AI]
- Category: Research

**Story 2**: "AI isn't replacing jobs. AI spending is"
- Score: 299
- Topics: [AI]
- Category: Industry

**Relationship**: Both share "AI" topic → connected with link

**Topic Node "AI"**:
- Mentions: 15
- Connected to 15 stories
- Large node due to high count

## Accessibility

- Semantic HTML structure
- ARIA labels on interactive elements
- Keyboard navigation supported
- High contrast colors
- Screen reader compatible

## Future Enhancements

Planned improvements:
1. Timeline slider to view evolution
2. Advanced filtering (date, score, source)
3. Search functionality
4. Network analysis metrics
5. Export as image/SVG
6. Share functionality
7. Bookmarking interesting patterns

---

## Try It Live!

Visit: https://enufacas.github.io/Chained/ai-knowledge-graph.html

The graph is live and updates automatically as new learnings are collected!
