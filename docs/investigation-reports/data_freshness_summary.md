# Data Freshness Report for Chained Repository

**Generated:** 2025-11-20 02:34:18 UTC

## Executive Summary

Total data files analyzed: **418 JSON/CSV files**

### Overall Status
- 🟢 **Episodes**: Fresh - latest is 1.9 hours old
- 🟡 **Learnings**: Mixed - some files 5-11 days old
- 🟢 **World State**: Fresh - recently updated
- 🟢 **Discussions**: 44 discussion files tracked

---

## Detailed Analysis by Category

### 📺 Episodes (docs/episodes/)
- **Total**: 75 episode files
- **Latest**: `episode-20251120-0041.json` (1.9 hours ago) ✅
- **Oldest**: `episode-20251113-0527.json` (6.9 days ago)
- **Status**: Episodes older than 7 days: 0 ✅
- **Recommendation**: Episode generation appears to be working correctly

### 📚 Learnings Files (learnings/)

#### Hacker News Learning
- **Total**: 26 files
- **Oldest**: `hn_20251109_190715.json` (11 days old)
- **Newest**: `hn_20251115_131749.json` (5 days old)
- ⚠️ **14 files older than 7 days** - Consider archiving or updating

#### TLDR Learning
- **Total**: 20 files
- **Oldest**: `tldr_20251109_082735.json` (11 days old)
- **Newest**: `tldr_20251115_082336.json` (5 days old)
- ⚠️ **11 files older than 7 days** - Consider archiving or updating

#### Analysis Files
- **Total**: 29 files
- **Date range**: 7 days to 1 day old
- **Status**: Relatively fresh ✅

#### Combined Analysis
- **Total**: 9 files
- **Date range**: 6 days to 1 day old
- **Status**: Relatively fresh ✅

#### Copilot Learning
- **Total**: 3 files
- **All**: 1 day old
- **Status**: Fresh ✅

#### GitHub Trending
- **Total**: 4 files
- **Date range**: 6 days to 5 days old
- **Status**: Could be refreshed 🟡

#### PR Analysis
- **PR Failures**: 5 files
- **PR Improvements**: 4 files
- **Status**: Active tracking ✅

### 💬 Discussions (learnings/discussions/)
- **Total**: 44 discussion files
- **Status**: Actively tracked ✅

### 🌍 World State (world/)
- Files appear to be tracked and updated
- Contains: `world_state.json`, `knowledge.json`, and pattern files
- **Status**: Active ✅

---

## 🎯 Recommendations

### Priority Actions

#### 1. Review Old Learning Files (Medium Priority)
**Issue**: 25 learning files (HN + TLDR) are older than 7 days
**Options**:
- **Option A**: Archive old files to a historical directory
- **Option B**: Enable/update the learning workflows to fetch fresh data
- **Option C**: Keep as-is if this is expected retention policy

**Affected Files**:
- 14 Hacker News files from Nov 9-15
- 11 TLDR files from Nov 9-15

**Recommendation**: Review if these old learning files are still needed or should be archived.

#### 2. GitHub Trending Updates (Low Priority)
**Issue**: GitHub trending files are 5-6 days old
**Action**: Consider updating the GitHub trending learning workflow if fresh trends are needed

#### 3. Verify Workflow Schedules (Info)
**Action**: Check if these workflows are scheduled or on-demand:
- HN learning workflow
- TLDR learning workflow  
- GitHub trending workflow

---

## Data Storage Overview

### Active Data Directories
1. **docs/episodes/** - 75 files (195 total in docs/)
2. **learnings/** - 141 files total
3. **world/** - 9 files (world state & knowledge)
4. **analysis/** - 47 files
5. **tools/data/** - 20 files
6. **.github/agent-system/** - System metadata

### Total Storage by Category
- **Episodes**: Most active, 2-hour refresh cycle ✅
- **Learnings**: Batch processing, 1-11 day age range 🟡
- **World State**: Active tracking ✅
- **Discussions**: Growing archive ✅

---

## Questions for Decision

1. **Old Learning Files**: Should files older than 7 days be:
   - [ ] Archived to a separate directory
   - [ ] Deleted
   - [ ] Kept as-is
   - [ ] Trigger refresh workflows

2. **Learning Workflow Status**: Are these workflows supposed to run daily?
   - [ ] Hacker News scraping
   - [ ] TLDR tech news
   - [ ] GitHub trending

3. **Retention Policy**: What's the intended retention for:
   - Episodes: Currently ~7 days
   - Learning files: Currently accumulating
   - Discussions: Currently accumulating

---

## Summary

✅ **Good**: Episode generation is working well (2-hour freshness)
✅ **Good**: Most analysis and combined analysis files are recent
✅ **Good**: World state appears actively maintained
🟡 **Review**: Some learning files (HN, TLDR) are 5-11 days old
🟡 **Review**: GitHub trending is 5-6 days stale

**Overall Assessment**: The repository's data pipeline is functioning, with most critical data (episodes, world state) being fresh. Some learning source files have aged, which may be expected behavior depending on workflow schedules.
