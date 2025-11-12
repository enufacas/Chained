# Agent Data Synchronization Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Agent System Data Flow                        │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────────────┐
│  Source of Truth         │
│  .github/agent-system/   │
│  registry.json           │
└────────────┬─────────────┘
             │
             │ (Trigger: on push to main)
             │
             ▼
┌──────────────────────────────────────┐
│  Agent Data Sync Workflow            │
│  .github/workflows/                  │
│  agent-data-sync.yml                 │
│                                      │
│  1. Copy full registry               │
│  2. Extract individual agents        │
│  3. Generate JSON files              │
│  4. Commit & push changes            │
└────────────┬─────────────────────────┘
             │
             │ (Output)
             │
             ▼
┌────────────────────────────────────────────┐
│  Published Data (docs/data/)               │
│                                            │
│  ├── agent-registry.json (full)           │
│  └── agents/                               │
│      ├── agent-1762852654.json            │
│      ├── agent-1762898916.json            │
│      ├── agent-1762901537.json            │
│      ├── agent-1762910779.json            │
│      ├── agent-1762918927.json            │
│      ├── agent-1762824870.json (HoF)      │
│      ├── agent-1762832596.json (HoF)      │
│      └── agent-1762842252.json (HoF)      │
└──────────────┬─────────────────────────────┘
               │
               │ (Consumed by)
               │
               ▼
┌──────────────────────────────────────┐
│  System Monitor Workflow             │
│  .github/workflows/                  │
│  system-monitor.yml                  │
│                                      │
│  Health Check 2:                     │
│  ✅ Verify docs/data/agents/        │
│     contains *.json files            │
└──────────────────────────────────────┘
```

## Data Synchronization Process

### Step 1: Registry Update
- Agent spawner creates/updates agents in registry
- Agent evaluator promotes/eliminates agents
- Registry stored in `.github/agent-system/registry.json`

### Step 2: Automatic Sync (Workflow Trigger)
```yaml
on:
  push:
    paths:
      - '.github/agent-system/registry.json'
    branches:
      - main
```

### Step 3: Data Extraction
```python
# Python script in agent-data-sync.yml
for agent in registry['agents']:
    agent_file = f'docs/data/agents/{agent_id}.json'
    json.dump(agent, agent_file)
```

### Step 4: Health Monitoring
```bash
# System monitor checks
if [ -d "docs/data/agents" ]; then
  agent_count=$(find docs/data/agents -name "*.json" | wc -l)
  if [ ${agent_count} -gt 0 ]; then
    echo "✅ Health check passed"
  fi
fi
```

## Before Fix

```
.github/agent-system/
└── registry.json (5 agents)

docs/data/
├── agent-registry.json
└── agents/
    └── (empty) ❌
```

**Result**: Health check fails (40% score)

## After Fix

```
.github/agent-system/
└── registry.json (5 agents)

docs/data/
├── agent-registry.json
└── agents/
    ├── agent-1762852654.json ✅
    ├── agent-1762898916.json ✅
    ├── agent-1762901537.json ✅
    ├── agent-1762910779.json ✅
    ├── agent-1762918927.json ✅
    ├── agent-1762824870.json ✅ (Hall of Fame)
    ├── agent-1762832596.json ✅ (Hall of Fame)
    ├── agent-1762842252.json ✅ (Hall of Fame)
    ├── README.md
    └── QUICK_REFERENCE.md
```

**Result**: Health check passes (60%+ score)

## Key Benefits

1. **Automated**: No manual file maintenance required
2. **Scalable**: Handles any number of agents
3. **Consistent**: Single source of truth (registry)
4. **Monitored**: Health checks verify sync is working
5. **Accessible**: Individual files enable easy API access

## Future Enhancements

- [ ] Add agent performance graphs
- [ ] Create agent comparison endpoints
- [ ] Generate agent leaderboards
- [ ] Add real-time status updates
- [ ] Build agent profile pages

---

*Documentation created by 📚 Lambda-1111 (doc-master)*
*Date: November 12, 2025*
