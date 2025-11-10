# 🧠 Continuous Learning

One of the most powerful features of Chained is its ability to **continuously learn** from external sources:

## Learning Sources

- **[TLDR Tech](https://tldr.tech/)**: Twice daily scraping of tech news summaries
- **[Hacker News](https://news.ycombinator.com/)**: Three times daily analysis of trending discussions

## What It Learns

The system automatically:
- 📰 Fetches latest tech news and articles
- 🎯 Identifies trending topics (AI/ML, Security, Performance, etc.)
- 💡 Extracts insights from community discussions
- 📊 Categorizes and prioritizes learnings
- 🔄 Feeds learnings back into idea generation

## Impact on Development

Learnings influence:
- **Idea Generation**: New ideas based on trending technologies
- **Technology Choices**: Adopting what's hot, avoiding what's deprecated
- **Best Practices**: Learning from the global tech community
- **Security**: Staying aware of vulnerabilities and fixes

See [`learnings/`](../learnings/) directory for all collected insights.

## Learning Workflow

```
Morning    → TLDR scraper runs     → Saves tech news
           → HN scraper runs        → Analyzes trending discussions
           → Smart Idea Generator   → Creates trend-aware ideas
Afternoon  → HN scraper runs again → Updates with new trends
Evening    → TLDR scraper runs     → Evening news update
           → HN scraper runs        → Final daily update
```

**The AI never stops learning from the world around it!** 🌍

---

[← Architecture](ARCHITECTURE.md) | [Back to README](../README.md) | [Tools →](TOOLS.md)
