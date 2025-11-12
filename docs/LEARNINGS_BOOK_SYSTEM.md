# 📖 Learnings Book System

This document describes the comprehensive learnings book system implemented in the Chained repository.

## Overview

The Learnings Book System transforms how the AI learns from external sources by:
1. **Fetching actual article content** from URLs (not just titles)
2. **Organizing learnings** into a structured book with chapters
3. **Daily reflection** to review and reinforce past learnings
4. **Inspiring idea generation** from organized knowledge

## Components

### 1. Web Content Fetcher (`tools/fetch-web-content.py`)

Fetches and extracts readable content from web pages.

**Features:**
- Handles common web scraping challenges (JavaScript, paywalls, formatting)
- Extracts clean, readable text from HTML
- Respects rate limits and robots.txt
- Returns structured JSON with title and content
- Supports batch fetching with delay

**Usage:**
```bash
# Fetch single URL
python3 tools/fetch-web-content.py "https://example.com"

# Fetch multiple URLs with output
python3 tools/fetch-web-content.py \
  "https://example.com/article1" \
  "https://example.com/article2" \
  --output results.json \
  --delay 2.0

# Custom timeout
python3 tools/fetch-web-content.py "https://example.com" --timeout 30
```

**Output format:**
```json
{
  "success": true,
  "url": "https://example.com",
  "title": "Article Title",
  "content": "Extracted article content...",
  "error": null
}
```

### 2. Learnings Book Builder (`tools/build-learnings-book.py`)

Reads learning JSON files and builds a structured book with chapters.

**Features:**
- Automatic categorization by topic (AI/ML, Programming, DevOps, etc.)
- Creates beautiful markdown files for each chapter
- Generates master index with statistics
- GitHub Pages compatible
- Updates automatically when new learnings arrive

**Usage:**
```bash
# Build book from default location
python3 tools/build-learnings-book.py

# Custom directories
python3 tools/build-learnings-book.py \
  --learnings-dir ./data/learnings \
  --book-dir ./docs/book
```

**Output:**
- `learnings/book/README.md` - Master index
- `learnings/book/AI_ML.md` - AI & Machine Learning chapter
- `learnings/book/Programming.md` - Programming chapter
- `learnings/book/DevOps.md` - DevOps chapter
- ... and more chapters

**Chapter structure:**
- Chapter title and description
- Total insights count
- Grouped by source (TLDR Tech, Hacker News)
- Each insight includes title, URL, content summary, and score

### 3. Enhanced Learning Workflows

#### `learn-from-tldr.yml`
- Runs twice daily (8 AM, 8 PM UTC)
- Fetches TLDR Tech RSS feeds (tech, ai, devops)
- **Reads actual article content** from links
- Saves JSON with full content
- Rebuilds learnings book
- Creates PR with changes

#### `learn-from-hackernews.yml`
- Runs three times daily (7 AM, 1 PM, 7 PM UTC)
- Fetches top 30 Hacker News stories
- Filters for high-quality (100+ upvotes)
- **Reads actual article content** from URLs
- Categorizes by topic
- Saves JSON with full content
- Rebuilds learnings book
- Creates PR with changes

### 4. Daily Learning Reflection (`daily-learning-reflection.yml`)

- Runs daily at 9 AM UTC
- Picks a random chapter from the learnings book
- Reviews key insights from that topic
- Creates reflection document
- Reinforces learning through active recall

**Output:**
- `learnings/reflection_YYYYMMDD.md` - Daily reflection document
- Issue documenting the reflection
- PR with reflection

### 5. Smart Idea Generator Integration (`idea-generator.yml`)

Enhanced to read from the learnings book:
- Checks for learnings book chapters
- Generates ideas based on specific chapter insights
- Creates learning-based ideas with book references
- Includes badge when inspired by the book

## Learnings Book Structure

```
learnings/
├── book/
│   ├── README.md           # Master index
│   ├── AI_ML.md            # AI & Machine Learning
│   ├── Programming.md      # Programming Languages
│   ├── DevOps.md           # DevOps & Infrastructure
│   ├── Database.md         # Databases
│   ├── Web.md              # Web Development
│   ├── Security.md         # Security & Privacy
│   ├── Performance.md      # Performance & Optimization
│   ├── Tools.md            # Developer Tools
│   └── OpenSource.md       # Open Source
├── hn_*.json               # Raw Hacker News data
├── tldr_*.json             # Raw TLDR Tech data
├── reflection_*.md         # Daily reflections
├── analysis_*.md           # Deep analysis reports
└── README.md               # Documentation
```

## Workflow Integration

```
┌──────────────────┐
│  TLDR Learning   │ ─┐  Fetches articles
│  (Twice daily)   │  │  + full content
└──────────────────┘  │
                      ├─► Learnings DB (JSON)
┌──────────────────┐  │
│  HN Learning     │  │  Fetches articles
│  (3x daily)      │ ─┘  + full content
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  Book Builder    │ ──► Organizes into chapters
│  (Automatic)     │     Learnings book (Markdown)
└──────────────────┘
         │
         ▼
┌──────────────────┐
│ Daily Reflection │ ──► Reviews & reflects
│  (9 AM UTC)      │     Reinforces learning
└──────────────────┘
         │
         ▼
┌──────────────────┐
│  Smart Idea Gen  │ ──► Reads learnings book
│  (10 AM UTC)     │     Generates enhanced ideas
└──────────────────┘
```

## Chapter Categories

### 🤖 AI & Machine Learning
Keywords: ai, ml, machine learning, neural, gpt, llm, copilot, openai, anthropic, model, training, transformer

### 💻 Programming Languages & Frameworks
Keywords: python, rust, go, javascript, typescript, java, c++, framework, library, language, code, compiler

### 🚀 DevOps & Infrastructure
Keywords: devops, docker, kubernetes, k8s, ci/cd, github actions, terraform, ansible, deployment, infrastructure

### 🗄️ Databases & Data Management
Keywords: database, sql, postgres, mysql, mongodb, redis, data, query, nosql, storage

### 🌐 Web Development
Keywords: web, browser, http, api, rest, graphql, react, vue, angular, frontend, backend

### 🔒 Security & Privacy
Keywords: security, vulnerability, encryption, auth, authentication, cve, exploit, privacy, breach

### ⚡ Performance & Optimization
Keywords: performance, optimization, speed, benchmark, fast, latency, throughput, efficient

### 🔧 Developer Tools
Keywords: tool, ide, editor, vscode, vim, debugger, git, productivity, workflow

### 🌟 Open Source & Community
Keywords: open source, oss, github, community, contribution, collaborative, license

### 📚 General Tech Insights
Catchall for learnings that don't fit other categories

## Benefits

1. **Rich Context**: Full article content, not just headlines
2. **Organized Knowledge**: Easy to browse by topic
3. **Active Learning**: Daily reflection reinforces insights
4. **Inspired Ideas**: Idea generation based on actual content
5. **GitHub Pages**: Beautiful web view of the book
6. **Automatic Updates**: Book rebuilds on new learnings
7. **Community Insights**: Both curated (TLDR) and community-driven (HN)

## Future Enhancements

Potential improvements to consider:
- Search functionality across the book
- Trend analysis over time
- Tag-based navigation
- Related insights linking
- Export to other formats (PDF, EPUB)
- Interactive visualizations
- Citation tracking

## Testing

To test the system:

```bash
# Test web content fetcher
python3 tools/fetch-web-content.py "https://example.com"

# Build the learnings book
python3 tools/build-learnings-book.py

# Check book structure
ls -la learnings/book/

# View a chapter
cat learnings/book/AI_ML.md

# View the index
cat learnings/book/README.md
```

## Troubleshooting

**Book not building:**
- Check that learning JSON files exist in `learnings/`
- Ensure Python dependencies are installed: `pip install beautifulsoup4 requests lxml html5lib`
- Run builder manually: `python3 tools/build-learnings-book.py`

**Web fetcher failing:**
- Some sites block scrapers (expected behavior)
- Check timeout settings
- Verify URL is accessible
- Check for SSL/certificate issues

**No content in learnings:**
- Content extraction may fail for some sites
- Paywalled articles won't have content
- Social media links are skipped intentionally

## Documentation

- Main learnings README: `learnings/README.md`
- Book index: `learnings/book/README.md`
- This document: `docs/LEARNINGS_BOOK_SYSTEM.md`

## Related Files

- `.github/workflows/learn-from-tldr.yml` - TLDR learning workflow
- `.github/workflows/learn-from-hackernews.yml` - HN learning workflow
- `.github/workflows/daily-learning-reflection.yml` - Daily reflection
- `.github/workflows/idea-generator.yml` - Enhanced idea generator
- `tools/fetch-web-content.py` - Web content fetcher
- `tools/build-learnings-book.py` - Book builder
- `learnings/README.md` - Learnings documentation
- `learnings/book/README.md` - Book index

---

*The Learnings Book System: Transforming how AI learns from the world.*
