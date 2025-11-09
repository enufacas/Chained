# Frequently Asked Questions (FAQ)

## General Questions

### What is Chained?

Chained is an experimental "perpetual AI motion machine" - a fully autonomous repository that generates ideas, creates issues, implements solutions, reviews code, and merges changes without human intervention.

### Is it really fully autonomous?

**Mostly, with one important caveat!**

The system operates autonomously for most tasks:
- ✅ Learns from external sources (TLDR Tech, Hacker News)
- ✅ Generates ideas based on learnings
- ✅ Creates GitHub issues automatically
- ✅ Converts issues to pull requests with task specifications
- ✅ Reviews and merges PRs automatically
- ✅ Tracks progress and health

**The Manual Step:** Currently, GitHub Copilot cannot be triggered programmatically. After a PR is created, you need to manually assign it to `@copilot-swe-agent` for actual code implementation. See [COPILOT_INTEGRATION.md](./COPILOT_INTEGRATION.md) for details.

**TL;DR**: Semi-autonomous - automates everything except the actual Copilot invocation step.

## Workflow and Automation Questions

### How does an issue actually get worked on after it's assigned to Copilot?

**The Short Answer:** Scheduled workflows prepare work, then you manually assign to Copilot.

**The Detailed Flow:**

1. **Issue Created** → Event trigger runs `copilot-assign.yml` immediately, adds "copilot-assigned" label
2. **Wait up to 30 minutes** → `issue-to-pr.yml` runs on schedule, creates a PR with task specification file
3. **Manual Step Required** → You assign the PR to `@copilot-swe-agent` (see [COPILOT_INTEGRATION.md](./COPILOT_INTEGRATION.md))
4. **Copilot Works** → Copilot analyzes task and makes code commits
5. **Wait up to 15 minutes** → `auto-review-merge.yml` runs on schedule, reviews and merges the PR
6. **Wait up to 30 minutes** → `auto-close-issues.yml` runs on schedule, closes the completed issue

**Key Insight:** Workflows automate PR preparation, but Copilot assignment is currently manual due to GitHub API limitations.

### What's forcing Copilot to do the work?

**Important Update:** Copilot is NOT automatically triggered by the workflows.

**What Actually Happens:**
- Scheduled workflows create PRs with task specifications
- These PRs contain `.copilot/task-{issue}.md` files describing what needs to be done
- Workflows @mention `@github-copilot` in comments (but this doesn't trigger work)
- **Manual step required**: You must assign the PR to `@copilot-swe-agent` to start actual implementation

**Why the Manual Step?**
- GitHub doesn't provide a public API to programmatically trigger Copilot agent sessions
- Simple @mentions in comments don't activate Copilot's autonomous work mode
- Assignment to `@copilot-swe-agent` is the only reliable way to trigger work

See [COPILOT_INTEGRATION.md](./COPILOT_INTEGRATION.md) for complete details and workarounds.

### Can I trust the cron schedules to actually run?

**Short Answer:** Mostly yes, with caveats.

**Long Answer:** GitHub Actions scheduled workflows are reliable but not guaranteed:

✅ **What works well:**
- Schedules run close to their defined times
- Workflows are triggered automatically without manual intervention
- GitHub has good uptime and reliability

⚠️ **Known limitations:**
- Minor delays (5-10 minutes) during GitHub's peak hours are normal
- Workflows are disabled after 60 days of repository inactivity
- GitHub doesn't guarantee exact execution times
- During high load, delays can be longer

**How to verify:** Use `./verify-schedules.sh` to check if workflows are running on time.

### What happens if a scheduled workflow doesn't run?

The system is designed to be **delay-tolerant**:

1. **Multiple workflows check for work** - If one misses a cycle, the next one will pick it up
2. **Work queues up** - Issues and PRs don't disappear; they wait for the next workflow run
3. **Monitoring alerts you** - `workflow-monitor.yml` detects and reports scheduling issues
4. **Manual fallback** - You can always trigger workflows manually via the Actions tab

**Bottom line:** Small delays don't break the system; work just progresses a bit slower.

### Why not use workflow_dispatch to chain workflows together?

**We tried that initially, but it had problems:**

- Requires `actions: write` permission
- Can trigger permission errors and 403 responses
- Creates tight coupling between workflows
- Harder to debug and monitor
- Can create infinite loops if not careful

**The scheduled approach is better because:**
- ✅ No permission issues
- ✅ Workflows are independent
- ✅ Easy to monitor and debug
- ✅ Self-correcting (missed work gets picked up later)
- ✅ Predictable timing

### How often do workflows actually run?

**Core Automation Workflows:**
- `auto-review-merge.yml`: Every 15 minutes
- `issue-to-pr.yml`: Every 30 minutes
- `auto-close-issues.yml`: Every 30 minutes

**Learning Workflows:**
- `learn-from-hackernews.yml`: 3 times daily (07:00, 13:00, 19:00 UTC)
- `learn-from-tldr.yml`: 2 times daily (08:00, 20:00 UTC)

**Idea Generation:**
- `idea-generator.yml`: Daily at 09:00 UTC
- `smart-idea-generator.yml`: Daily at 10:00 UTC

**Monitoring:**
- `timeline-updater.yml`: Every 6 hours
- `progress-tracker.yml`: Every 12 hours
- `workflow-monitor.yml`: Every 12 hours

**To verify actual run times:** Run `./verify-schedules.sh`

### What if I need faster turnaround?

You have options:

1. **Manually trigger workflows** - Go to Actions tab → Select workflow → "Run workflow"
2. **Adjust schedules** - Edit the cron expressions in `.github/workflows/*.yml`
3. **Add event triggers** - Supplement schedules with event-based triggers
4. **Use workflow_dispatch** - Set up manual or API-triggered workflows

However, be aware that:
- Very frequent schedules (< 5 minutes) may hit GitHub rate limits
- More frequent runs consume more Actions minutes
- The current intervals are designed to balance responsiveness with resource usage

### How do I know if schedules are actually running?

**Multiple ways to check:**

1. **Run the verification script:**
   ```bash
   ./verify-schedules.sh
   ```
   Shows when each workflow last ran and if it's on schedule.

2. **Check the Actions tab:**
   - Go to your repository → Actions
   - Filter by workflow name
   - See recent runs and their status

3. **Monitor workflow-monitor issues:**
   - The system creates issues when it detects scheduling problems
   - Look for issues labeled "workflow-monitor"

4. **Check GitHub Pages timeline:**
   - Visit https://yourusername.github.io/Chained/
   - Shows recent activity and autonomous actions

5. **Run the status script:**
   ```bash
   ./check-status.sh
   ```
   Shows recent workflow runs and metrics.

## Troubleshooting Questions

### A workflow didn't run at its scheduled time. What should I do?

1. **Wait 10-20 minutes** - Minor delays are normal
2. **Check the Actions tab** - See if the workflow ran late
3. **Look for errors** - Check if the workflow failed rather than not running
4. **Check for 60-day deactivation** - Run `./verify-schedules.sh` to see if repository is inactive
5. **Manually trigger** - Go to Actions → Select workflow → "Run workflow"

### My schedules haven't run in days. What's wrong?

**Possible causes:**

1. **60-day inactivity** - Scheduled workflows are disabled after 60 days of no repository activity
   - **Solution:** Make a commit or create activity to re-enable them
   
2. **Workflows are disabled** - Someone manually disabled them in the Actions tab
   - **Solution:** Go to Actions → Enable workflows

3. **GitHub incident** - Rare but possible
   - **Solution:** Check https://www.githubstatus.com/

4. **Permission issues** - Workflow doesn't have required permissions
   - **Solution:** Review workflow permissions in the YAML file

**Quick check:** Run `./verify-schedules.sh` to diagnose.

### How do I manually trigger a workflow?

**Via GitHub UI:**
1. Go to your repository's **Actions** tab
2. Click on the workflow you want to run (left sidebar)
3. Click the **"Run workflow"** button (top right)
4. Select the branch (usually "main")
5. Fill in any required inputs (if applicable)
6. Click **"Run workflow"** to confirm

**Via GitHub CLI:**
```bash
gh workflow run "workflow-name.yml"
```

Or for a specific workflow with inputs:
```bash
gh workflow run "issue-to-pr.yml" -f issue_number=42
```

### A workflow failed. Should I be concerned?

**It depends:**

- **Occasional failures** - Normal, often due to transient issues
- **Repeated failures** - Worth investigating
- **Critical workflow failures** - `workflow-monitor.yml` will alert you

**Check the logs:**
1. Go to Actions → Click on the failed run
2. Review the error messages
3. Common issues:
   - No work to do (not actually an error)
   - API rate limits (wait and retry)
   - Permission errors (check workflow permissions)
   - Merge conflicts (resolve manually)

**The system is self-healing** - monitoring will detect patterns and alert you.

### What's the 60-day deactivation thing?

GitHub automatically disables scheduled workflows in public repositories that have been inactive for 60 days.

**To check your status:**
```bash
./verify-schedules.sh
```

**To prevent deactivation:**
- Make commits regularly
- Create issues or PRs
- Manually trigger workflows
- Keep the autonomous cycle running (it creates activity)

**To re-enable after deactivation:**
1. Make any commit to the repository
2. Go to Actions → Enable workflows
3. Workflows will resume their schedules

## Configuration Questions

### Can I change the schedule frequencies?

**Yes!** Edit the workflow files in `.github/workflows/`:

```yaml
on:
  schedule:
    - cron: '*/30 * * * *'  # Change this line
```

**Cron syntax:**
- `*/15 * * * *` - Every 15 minutes
- `*/30 * * * *` - Every 30 minutes
- `0 */6 * * *` - Every 6 hours
- `0 9 * * *` - Daily at 9 AM UTC

**Recommendations:**
- Don't go below 5-minute intervals (may hit rate limits)
- Consider Actions minutes usage for frequent schedules
- Balance responsiveness with resource consumption

### Can I add more workflows?

Absolutely! The system is extensible:

1. Create a new workflow file in `.github/workflows/`
2. Define your trigger (schedule, event, or manual)
3. Add the necessary permissions
4. Implement your logic
5. Commit and push

The `workflow-monitor.yml` will automatically start tracking it.

### How do I customize what ideas get generated?

**Edit these files:**
- `.github/workflows/idea-generator.yml` - Basic idea generation
- `.github/workflows/smart-idea-generator.yml` - Learning-influenced ideas

**Modify:**
- The prompts used to generate ideas
- The topics and themes
- The frequency of generation
- The labels applied to issues

## Monitoring Questions

### How do I know the system is working?

**Multiple indicators:**

1. **GitHub Pages timeline updates** - Should show regular activity
2. **New issues created** - Look for "ai-generated" label
3. **PRs created and merged** - Check the PRs tab
4. **Workflow runs** - Actions tab shows recent runs
5. **No workflow-monitor issues** - Indicates health

**Quick check:**
```bash
./check-status.sh
```

### What do the different labels mean?

- **ai-generated** - Issue was created by AI idea generator
- **copilot-assigned** - Issue is assigned to Copilot for work
- **copilot** - PR or content created by Copilot
- **automated** - Action was automated (not manual)
- **in-progress** - Work is currently being done
- **completed** - Work is finished and verified
- **learning** - Contains learnings or insights
- **progress-report** - Progress tracking information
- **workflow-monitor** - Alert about workflow health issues

### What should I do if I see a workflow-monitor issue?

1. **Read the issue** - It contains diagnostic information
2. **Check the Actions tab** - Review recent workflow runs
3. **Run verification** - `./verify-schedules.sh` for current status
4. **Take recommended actions** - The issue provides specific guidance
5. **Close when resolved** - System will reopen if problems persist

## Advanced Questions

### Can I deploy this to my own repository?

**Yes!** See [GETTING_STARTED.md](./GETTING_STARTED.md) for setup instructions.

**Key steps:**
1. Fork or clone the repository
2. Enable Actions in your repository settings
3. Enable GitHub Pages (Settings → Pages → /docs)
4. Run `./validate-system.sh` to verify setup
5. Run `./kickoff-system.sh` or merge to main to start

### Does this work with private repositories?

**Yes, but with considerations:**

- ✅ All workflows work the same
- ✅ Actions minutes usage counts against your quota
- ⚠️ 60-day deactivation still applies
- ⚠️ GitHub Pages may require a paid plan

### Can I use this for real development work?

**Sort of.** Chained is primarily an **educational and experimental demonstration**.

**Good for:**
- Learning about autonomous systems
- Experimenting with AI-driven development
- Demonstrations and teaching
- Low-stakes projects
- Documentation and learnings repositories

**Not ideal for:**
- Production code with quality requirements
- Sensitive or security-critical projects
- Projects requiring human review and approval
- Compliance-regulated codebases

**However:** You could adapt the concepts for:
- Automated documentation updates
- Learning and insight collection
- Routine maintenance tasks
- Automated testing and reporting

### How much does this cost in Actions minutes?

**Estimates for a typical day:**

- Learning workflows: ~5 minutes total
- Idea generation: ~2 minutes
- Issue to PR: ~5 minutes (if processing issues)
- Auto review/merge: ~10 minutes (depends on PR count)
- Monitoring: ~5 minutes

**Total:** ~25-30 minutes per day on average

**Public repositories:** Free unlimited minutes
**Private repositories:** Counts against your monthly quota (2,000-3,000 minutes/month depending on plan)

### Can I contribute to Chained?

**Yes!** Contributions are welcome:

1. **External PRs** require manual review (security policy)
2. **Suggest ideas** - Open issues with enhancement suggestions
3. **Improve workflows** - Submit PRs to enhance automation
4. **Report issues** - Help identify bugs or problems
5. **Share learnings** - Document what you discover

See the Contributing section in README.md.

## Getting Help

### Where can I find more information?

**Documentation:**
- [README.md](./README.md) - Overview and architecture
- [WORKFLOW_TRIGGERS.md](./WORKFLOW_TRIGGERS.md) - How workflows are triggered
- [AUTONOMOUS_CYCLE.md](./AUTONOMOUS_CYCLE.md) - Detailed cycle documentation
- [GETTING_STARTED.md](./GETTING_STARTED.md) - Setup instructions

**Tools:**
- `./check-status.sh` - System status overview
- `./verify-schedules.sh` - Schedule verification
- `./validate-system.sh` - Pre-flight checks

### Something's not covered here. What should I do?

1. **Check existing issues** - Search for similar questions
2. **Review documentation** - Check the docs/ directory
3. **Open an issue** - Ask your question
4. **Check workflow logs** - Often contains diagnostic info

## Summary

**Key Takeaways:**

✅ **Schedules are reliable** - GitHub Actions cron schedules work well with minor delays
✅ **Trust but verify** - Use `./verify-schedules.sh` to confirm execution
✅ **System is self-healing** - Monitoring detects and reports issues
✅ **Manual fallback** - You can always trigger workflows manually
✅ **Delay-tolerant** - Small timing variations don't break the cycle

**The autonomous system is designed to "just work" with minimal intervention.**
