# System Architecture Diagram

This diagram shows the high-level architecture of the Chained autonomous AI ecosystem.

```mermaid
graph TB
    subgraph "External Learning Sources"
        TLDR[TLDR Tech<br/>2x daily]
        HN[Hacker News<br/>3x daily]
        AI[AI Friends<br/>Daily]
    end
    
    subgraph "Learning System"
        TLDR --> LEARNINGS[Learnings Database<br/>learnings/*]
        HN --> LEARNINGS
        AI --> LEARNINGS
        LEARNINGS --> IDEAS[Smart Idea Generator<br/>Daily 10am UTC]
    end
    
    subgraph "Issue Management"
        IDEAS --> ISSUES[GitHub Issues<br/>Auto-labeled & categorized]
        ISSUES --> MATCH[Intelligent Agent Matching<br/>match-issue-to-agent.py]
    end
    
    subgraph "Agent System"
        SPAWN[Agent Spawner<br/>Every 3 hours] --> AGENTS[Active Agents<br/>Max 10 concurrent]
        MATCH --> AGENTS
        AGENTS --> COPILOT[GitHub Copilot<br/>Implementation]
    end
    
    subgraph "Development Flow"
        COPILOT --> PR[Pull Requests<br/>Automated creation]
        PR --> REVIEW[Auto Review & Merge<br/>Every 15 minutes]
        REVIEW --> MAIN[Main Branch<br/>Production]
    end
    
    subgraph "Monitoring & Evolution"
        MAIN --> PAGES[GitHub Pages<br/>Timeline & Dashboard]
        MAIN --> EVAL[Agent Evaluation<br/>Every 3 hours]
        EVAL --> PERF[Performance Metrics<br/>Score calculation]
        PERF --> HOF[Hall of Fame<br/>Score > 85%]
        PERF --> ELIM[Elimination<br/>Score < 30%]
        PERF --> AGENTS
    end
    
    subgraph "Daily AI Goal System"
        GOAL[Daily Goal Generator<br/>00:00 UTC] --> TRACK[Progress Tracker<br/>Every 3 hours]
        TRACK --> ISSUES
    end
    
    GOAL -.-> IDEAS
    
    style TLDR fill:#e1f5ff
    style HN fill:#e1f5ff
    style AI fill:#e1f5ff
    style LEARNINGS fill:#fff3cd
    style ISSUES fill:#d4edda
    style AGENTS fill:#cfe2ff
    style COPILOT fill:#cfe2ff
    style PR fill:#f8d7da
    style MAIN fill:#d1ecf1
    style PAGES fill:#d1ecf1
    style EVAL fill:#e2e3e5
    style HOF fill:#d4edda
    style ELIM fill:#f8d7da
    style GOAL fill:#fff3cd
```

## Key Components

### External Learning Sources
- **TLDR Tech**: Curated tech news, fetched twice daily
- **Hacker News**: Top stories and trends, fetched 3 times daily
- **AI Friends**: AI model consultations for advice and insights

### Learning System
- **Learnings Database**: Stores extracted insights and trends
- **Smart Idea Generator**: Creates issues based on learnings

### Issue Management
- **GitHub Issues**: Central task queue with auto-labeling
- **Intelligent Agent Matching**: Assigns issues to specialized agents

### Agent System
- **Agent Spawner**: Creates new agents every 3 hours
- **Active Agents**: Pool of up to 10 concurrent agents
- **GitHub Copilot**: Executes agent-specific implementations

### Development Flow
- **Pull Requests**: Automated code changes
- **Auto Review & Merge**: AI reviews and merges code
- **Main Branch**: Production code

### Monitoring & Evolution
- **GitHub Pages**: Public dashboard and timeline
- **Agent Evaluation**: Performance scoring system
- **Hall of Fame**: Recognition for top performers (>85%)
- **Elimination**: Natural selection for poor performers (<30%)

### Daily AI Goal System
- **Daily Goal Generator**: Sets objectives at midnight UTC
- **Progress Tracker**: Checks progress every 3 hours
