# 🧠 Learnings Directory

This directory contains insights and learnings collected from external sources to help the AI continuously improve.

## Sources

### TLDR Tech (https://tldr.tech/)
- **Frequency**: Twice daily (8 AM, 8 PM UTC)
- **Content**: Tech news summaries, AI updates, DevOps trends
- **Format**: `tldr_YYYYMMDD_HHMMSS.json`

### Hacker News (https://news.ycombinator.com/)
- **Frequency**: Three times daily (7 AM, 1 PM, 7 PM UTC)
- **Content**: Top technical discussions, trending topics, community insights
- **Format**: `hn_YYYYMMDD_HHMMSS.json`

## Learning Structure

Each learning file contains:
```json
{
  "timestamp": "ISO 8601 timestamp",
  "source": "TLDR Tech or Hacker News",
  "learnings": [
    {
      "title": "Article/story title",
      "description": "Brief description",
      "url": "Link to full content",
      "score": "Relevance score (HN only)"
    }
  ],
  "topics": {
    "AI/ML": ["Related titles..."],
    "Programming": ["Related titles..."],
    ...
  },
  "trends": ["Extracted trend statements"]
}
```

## How Learnings Are Used

The autonomous system uses these learnings to:

1. **Enhance Idea Generation**
   - Smart Idea Generator reads recent learnings
   - Generates ideas based on trending topics
   - Prioritizes technologies gaining traction

2. **Inform Implementation Decisions**
   - Choose modern approaches over outdated ones
   - Adopt emerging best practices
   - Integrate trending tools and frameworks

3. **Track Technology Evolution**
   - Monitor shifts in the tech ecosystem
   - Identify declining vs. rising technologies
   - Adapt to community preferences

4. **Continuous Improvement**
   - Learn from successful patterns in the wild
   - Avoid anti-patterns discussed in communities
   - Stay current with security vulnerabilities

## Learning Index

`index.json` contains aggregate statistics:
- Total learnings collected
- Learnings per source
- Most common topics
- Last update timestamp

## Workflow Integration

```
┌──────────────────┐
│  TLDR Learning   │ ─┐
│  (Twice daily)   │  │
└──────────────────┘  │
                      ├─► Learnings DB
┌──────────────────┐  │
│  HN Learning     │  │
│  (3x daily)      │ ─┘
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  Smart Idea Gen  │ ──► Reads learnings
│  (Daily at 10AM) │     Generates enhanced ideas
└──────────────────┘

```

## Benefits

This learning system enables the AI to:
- 🎯 Stay relevant with current tech trends
- 🚀 Adopt emerging technologies quickly
- 🛡️ Respond to security threats proactively
- 📈 Improve over time through external knowledge
- 🌍 Learn from the global tech community

## Example Learning Flow

1. **Morning** (8 AM UTC): TLDR scraper runs
   - Collects latest tech news
   - Saves to `tldr_20231109_080000.json`
   - Creates learning issue documenting insights

2. **Later Morning** (10 AM UTC): Smart Idea Generator runs
   - Reads recent learning files
   - Identifies AI/ML trend in learnings
   - Generates: "Build an LLM-powered code assistant based on recent AI trends"
   - Creates issue with learning context

3. **Afternoon** (1 PM UTC): HN scraper runs
   - Analyzes top HN stories
   - Finds performance optimization discussions
   - Saves topics for future idea generation

4. **Continuous**: Ideas incorporate learnings
   - Each idea considers recent trends
   - Implementation uses modern approaches
   - System evolves with the ecosystem

## Viewing Learnings

Learning issues are automatically created with the `learning` label:
- View all: Filter issues by `learning` label
- Recent: Sort by newest first
- Timeline: Check GitHub Pages for visual representation

## Privacy & Ethics

- Only public content is accessed (RSS feeds, public APIs)
- No user data or tracking is involved
- Content is used for learning, not reproduction
- Full attribution to sources is maintained

---

**The AI never stops learning.** 🚀
