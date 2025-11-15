# World Model System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CHAINED WORLD MODEL                          │
│                Geographic Autonomous AI Exploration                  │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐         ┌──────────────────────────┐
│   EXTERNAL SOURCES      │         │   GITHUB ACTIONS         │
│                         │         │                          │
│  • Tech Articles        │         │  world-update.yml        │
│  • TLDR News           │──┐      │  (Every 2 hours)         │
│  • Hacker News         │  │      │                          │
└─────────────────────────┘  │      └────────┬─────────────────┘
                             │               │
                             ▼               ▼
                    ┌────────────────────────────────┐
                    │   ARTICLE INGESTION PIPELINE   │
                    │   scripts/ingest_article.py    │
                    │                                │
                    │  • Extract companies           │
                    │  • Map to HQ locations         │
                    │  • Identify patterns           │
                    │  • Generate inspiration regions│
                    └────────┬───────────────────────┘
                             │
                             ▼
             ┌───────────────────────────────────┐
             │        WORLD STATE LAYER          │
             │                                   │
             │  ┌──────────────────────────┐    │
             │  │  world_state.json        │    │
             │  │  • Agents                │    │
             │  │  • Regions               │    │
             │  │  • Objectives            │    │
             │  │  • Metrics               │    │
             │  └──────────────────────────┘    │
             │                                   │
             │  ┌──────────────────────────┐    │
             │  │  knowledge.json          │    │
             │  │  • Ideas                 │    │
             │  │  • Companies             │    │
             │  │  • Inspiration regions   │    │
             │  └──────────────────────────┘    │
             └───────┬───────────────────────────┘
                     │
                     ├────────────────────┬────────────────────┐
                     ▼                    ▼                    ▼
         ┌─────────────────────┐ ┌────────────────┐ ┌──────────────────┐
         │  STATE MANAGER      │ │ KNOWLEDGE MGR  │ │ AGENT NAVIGATOR  │
         │                     │ │                │ │                  │
         │  • Load/save state  │ │ • Add ideas    │ │ • Build paths    │
         │  • Update agents    │ │ • Query ideas  │ │ • Move agents    │
         │  • Manage regions   │ │ • Count ideas  │ │ • Select ideas   │
         └─────────────────────┘ └────────────────┘ └──────────────────┘
                     │
                     ▼
         ┌───────────────────────────┐
         │   AGENT UPDATE SYSTEM     │
         │   scripts/update_agent.py │
         │                           │
         │  1. Load world & ideas    │
         │  2. Assign idea to agent  │
         │  3. Build navigation path │
         │  4. Move agent one step   │
         │  5. Update metrics        │
         │  6. Save state            │
         └───────────┬───────────────┘
                     │
                     ▼
         ┌───────────────────────────────────┐
         │      VISUALIZATION LAYER          │
         │      docs/world-map.html          │
         │      docs/world-map.js            │
         │                                   │
         │  ┌──────────────────────────┐    │
         │  │   Leaflet.js Map         │    │
         │  │   • OpenStreetMap tiles  │    │
         │  │   • Region circles       │    │
         │  │   • Agent markers        │    │
         │  │   • Interactive popups   │    │
         │  └──────────────────────────┘    │
         │                                   │
         │  ┌──────────────────────────┐    │
         │  │   Metrics Sidebar        │    │
         │  │   • Tick counter         │    │
         │  │   • Total ideas          │    │
         │  │   • Total regions        │    │
         │  │   • Agent status         │    │
         │  └──────────────────────────┘    │
         └───────────────────────────────────┘
                         │
                         ▼
              ┌──────────────────────┐
              │   GITHUB PAGES       │
              │   Auto-deployed      │
              │   Live at:           │
              │   enufacas.github.io │
              └──────────────────────┘


═══════════════════════════════════════════════════════════════════

DATA FLOW EXAMPLE:

1. Article: "OpenAI launches GPT-5 with CI automation"
   ↓
2. Ingestion extracts: OpenAI (SF), Microsoft (Redmond), GitHub (SF)
   ↓
3. Creates inspiration regions:
   • US:San Francisco (weight: 0.67)
   • US:Redmond (weight: 0.33)
   ↓
4. Adds idea to knowledge.json
   ↓
5. Updates world_state.json with new regions
   ↓
6. Agent update assigns idea to agent
   ↓
7. Agent builds path: [San Francisco, Redmond]
   ↓
8. Agent moves one step per tick
   ↓
9. Map visualizes agent traveling between cities
   ↓
10. Cycle repeats every 2 hours

═══════════════════════════════════════════════════════════════════

KEY FEATURES:

✅ Geographic mapping of ideas to real-world locations
✅ Autonomous agent navigation between inspiration regions
✅ Real-time interactive world map visualization
✅ Automated updates via GitHub Actions (every 2 hours)
✅ Modular Python architecture
✅ JSON-based persistence (merge-conflict resistant)
✅ Comprehensive testing and documentation
✅ Zero security vulnerabilities
✅ Fully integrated with existing Chained ecosystem

═══════════════════════════════════════════════════════════════════
```
