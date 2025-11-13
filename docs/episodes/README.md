# Chained TV Episodes

This directory contains episodic stories automatically generated from repository activity.

## 📺 Overview

Chained TV transforms repository activity (Issues, Pull Requests, commits) into narrative episodes with scenes, characters, and dialogue. It's like a TV show about your repository!

## 🎬 Episode Format

Each episode is a JSON file with the following structure:

```json
{
  "date": "ISO timestamp",
  "title": "Episode title",
  "scenes": [
    {
      "bg": "night|alert|calm|lab",
      "narration": "Scene description",
      "characters": [
        {
          "name": "Character name",
          "side": "left|right|center",
          "mood": "determined|smug|angry|worried|happy",
          "line": "Character dialogue"
        }
      ]
    }
  ]
}
```

## 📁 Files

- **`latest.json`** - The most recent episode, always up to date
- **`episode-YYYYMMDD-HHMM.json`** - Timestamped episodes (archived)
- **`demo-episode.json`** - Demo episode showing typical activity

## 🎭 Story Elements

### Backgrounds

Episodes use different backgrounds to set the mood:
- **`night`** - Dark, mysterious, for ongoing work
- **`alert`** - Red-tinted, urgent, for issues and failures
- **`calm`** - Blue-green, peaceful, for success and resolution
- **`lab`** - Purple-blue, technical, for development work

### Characters

Characters represent different actors in the repository:
- **Developers** - Real GitHub users who create PRs and issues
- **Merge Oracle** - Celebrates successful merges
- **Code Reviewer** - Reviews pull requests
- **Issue Hunter** - Tracks and resolves issues
- **Build Guardian** - Monitors CI/CD and builds
- **System Monitor** - Watches overall repository health

### Moods

Characters express emotions through their mood:
- **`determined`** - Blue, focused and driven
- **`smug`** - Purple, satisfied and confident
- **`angry`** - Red, frustrated or urgent
- **`worried`** - Orange, concerned or anxious
- **`happy`** - Green, pleased and successful

## 🚀 Generation

Episodes are generated automatically:
- **Schedule**: Every 2 hours via GitHub Actions
- **Script**: `scripts/generate_episode.py`
- **Workflow**: `.github/workflows/chained_tv.yml`

You can also trigger generation manually:
1. Go to Actions tab
2. Select "Chained TV Episode Generator"
3. Click "Run workflow"

## 👁️ Viewing

To watch episodes:

**Latest Episode**: Visit https://enufacas.github.io/Chained/tv.html

**Episode Archive**: Browse all episodes by date at https://enufacas.github.io/Chained/episodes.html

**Specific Episode**: Use `tv.html?episode=episode-YYYYMMDD-HHMM.json` to view a particular episode

The viewer features:
- Animated scene transitions
- Character avatars with glowing effects
- Speech bubbles with dialogue
- Episode archive with day-by-day browsing
- Responsive design for all devices

## 🏷️ Auto-Merge Requirements

For Chained TV PRs to automatically merge, they must have these labels:
- `chained-tv` ✓
- `automated` ✓
- `copilot` ✓ (added November 2025)

The workflow now automatically adds all three labels. If you have old PRs that aren't merging, run:

```bash
bash scripts/cleanup-chained-tv-prs.sh
```

This will add the `copilot` label to existing PRs and close stale ones (>24 hours old).

## 📊 Activity Mapping

The generator creates different scenes based on repository activity:

| Activity | Scene Type |
|----------|-----------|
| Merged PR | Success scene with Merge Oracle |
| Open PR | Work-in-progress with reviewers |
| Closed PR (unmerged) | Failure/learning scene |
| Closed Issue | Victory scene with Issue Hunter |
| Open Issue | Alert scene with call to action |
| No activity | Calm "standby" scene |

## 🎨 Example Episode

Here's what a typical episode looks like:

**Title**: "Merge Victory"

**Scene 1** (Lab):
> *In the last 2 hours, 4 events unfolded in the Chained repository...*
> 
> **Build Guardian**: "I've tracked 2 pull requests. Let's see what stories they tell."

**Scene 2** (Calm):
> *PR #138 has been merged successfully. 50 lines added, 30 removed.*
> 
> **Merge Oracle**: "The merge is complete. Well done, enufacas."

**Scene 3** (Night):
> *PR #141 awaits review. The code hangs in the balance.*
> 
> **copilot** (worried): "I hope the reviewers like my changes..."
> **Code Reviewer** (determined): "Let me examine this carefully. Quality matters."

## 🔧 Technical Details

- **Language**: Python 3.12+
- **Dependencies**: `requests` (for GitHub API)
- **API**: GitHub REST API v3
- **Format**: JSON (pretty-printed)
- **Viewer**: Vanilla HTML/CSS/JavaScript

## 📝 Contributing

To modify episode generation:

1. Edit `scripts/generate_episode.py`
2. Add new scene types, characters, or story logic
3. Update this README with new features
4. Test with `python tests/test_chained_tv.py`

To customize the viewer:

1. Edit `docs/tv.html`
2. Modify CSS styles in the `<style>` section
3. Update JavaScript in the `<script>` section
4. Test locally with a web server

## 🎯 Philosophy

Chained TV makes repository activity more engaging and human by:
- Transforming dry logs into narratives
- Giving identity to developers and bots
- Creating emotional context for technical work
- Making the repository feel alive and dynamic

It's automation that tells stories! 📖✨

---

*Generated by the Chained autonomous AI ecosystem*
