# Chained Repository Configuration

## Branch Protection Settings

To enable fully autonomous operation for owner/Copilot while requiring review for external contributions:

1. Go to Repository Settings → Branches
2. Add a branch protection rule for `main`:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (1 approval required)
   - ✅ Require review from Code Owners
   - ⚠️ **CHECK** "Allow specified actors to bypass required pull requests" and add:
     - `github-actions[bot]` (for autonomous Copilot workflows)
   - ✅ Allow auto-merge
   - ✅ Automatically delete head branches
   - Optional: Require status checks to pass (if you have CI)

**Security Note:** This configuration ensures:
- External contributions require owner review (via CODEOWNERS)
- Owner's Copilot-labeled PRs can auto-merge (via auto-review-merge workflow)
- Bot-created PRs with copilot label can auto-merge (via auto-review-merge workflow)
- All other PRs require manual review and approval

## Workflow Permissions

Ensure workflows have the necessary permissions:

1. Go to Repository Settings → Actions → General
2. Under "Workflow permissions":
   - Select "Read and write permissions"
   - ✅ Check "Allow GitHub Actions to create and approve pull requests"

## GitHub Pages

Enable GitHub Pages to publish the timeline:

1. Go to Repository Settings → Pages
2. Under "Build and deployment":
   - Source: **Deploy from a branch**
   - Branch: **main** (or your default branch)
   - Folder: **/docs**
3. Click **Save**

## Labels

The system uses these labels automatically. **For comprehensive documentation on all labels, see [LABELS.md](./LABELS.md)** which includes detailed explanations, usage examples, and workflows.

**Core labels:**
- `ai-generated` - Issues created by the AI Idea Generator
- `copilot-assigned` - Issues assigned to Copilot
- `copilot` - PRs created by automated systems
- `automated` - Automated actions
- `in-progress` - Work currently being done
- `completed` - Finished tasks
- `learning` - Insights and learnings
- `progress-report` - Progress tracking issues

**Note:** The difference between `copilot-assigned` (issue assigned TO Copilot) and `copilot` (content created BY Copilot) is critical for auto-merge functionality. See [LABELS.md](./LABELS.md) for details.

## Scheduled Workflows

The autonomous system runs on these schedules:
- **Idea Generator**: Daily at 9 AM UTC
- **Smart Idea Generator**: Daily at 10 AM UTC
- **Learn from TLDR**: 2x daily (8 AM, 8 PM UTC)
- **Learn from Hacker News**: 3x daily (7 AM, 1 PM, 7 PM UTC)
- **Auto Review & Merge**: Every 15 minutes
- **Issue to PR**: Every 30 minutes
- **Auto Close Issues**: Every 30 minutes
- **Timeline Updater**: Every 6 hours
- **Progress Tracker**: Every 12 hours
- **Workflow Monitor**: Every 12 hours

All workflows can also be triggered manually via the Actions tab.

## Optional: Custom Domain

To use a custom domain for GitHub Pages:
1. Add a CNAME file in the docs/ directory
2. Configure DNS settings with your domain provider
3. Update the domain in Repository Settings → Pages

## Security Considerations

This repository is designed for autonomous AI development while maintaining security:

### Protection Against External Contributions
- **CODEOWNERS file**: Requires repository owner review for all changes
- **Auto-merge restrictions**: Only owner or trusted bot PRs with `copilot` label can auto-merge
- **Branch protection**: Configured to require review from code owners

### Autonomous Operation
The system maintains full autonomy for:
- Repository owner's Copilot-generated PRs (with `copilot` label)
- Trusted bot PRs (github-actions[bot], dependabot[bot], copilot) with `copilot` label

### For Production Use
Additional considerations:
- Add required status checks before merge
- Implement comprehensive testing
- Add code scanning and security analysis
- Consider limiting auto-merge to specific branches
- Review automated changes periodically
- Monitor for unusual PR patterns

## Protected Agents

Some agents in the system are designated as **protected** and cannot be eliminated through the normal evaluation process.

### What are Protected Agents?

Protected agents are critical agents that:
- 🛡️ **Cannot be deleted**: They are permanent fixtures in the system
- 🗳️ **Cannot be voted off**: They are immune to elimination based on performance
- 🎯 **Fill essential roles**: Their specialization is critical to system health
- 📊 **Still tracked**: Their performance metrics are monitored for recognition

### Current Protected Agents

- **🔧 troubleshoot-expert**: Essential for maintaining GitHub Actions and workflow health. This agent has specialized tools for debugging CI/CD issues.

### How to Add Protected Agents

To designate an agent as protected:

1. Create the agent definition in `.github/agents/[agent-name].md` following the standard convention
2. Add the agent's name to the `protected_specializations` array in `.github/agent-system/registry.json`:
   ```json
   "config": {
     "protected_specializations": [
       "troubleshoot-expert",
       "your-new-protected-agent"
     ]
   }
   ```
3. Document the agent's protected status in its definition file
4. Update `.github/agents/README.md` to indicate the agent is protected (🛡️)
5. Update `.github/agent-system/README.md` to list the new protected agent

### When to Make an Agent Protected

Consider making an agent protected if:
- The agent provides critical infrastructure or monitoring
- The agent's specialization is essential to system operations
- Losing the agent would create a significant gap in capabilities
- The agent handles emergency or high-priority issues

**Note:** Use protected status sparingly. Most agents should participate in the normal evaluation and elimination process to maintain the competitive ecosystem.
