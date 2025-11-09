# Chained Repository Configuration

## Branch Protection Settings

To enable fully autonomous operation without human review:

1. Go to Repository Settings → Branches
2. Add a branch protection rule for `main`:
   - ✅ Require a pull request before merging
   - ⚠️ **UNCHECK** "Require approvals" (to allow auto-merge)
   - ✅ Allow auto-merge
   - ✅ Automatically delete head branches
   - Optional: Require status checks to pass (if you have CI)

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

The system uses these labels automatically:
- `ai-generated` - Issues created by the AI Idea Generator
- `copilot-assigned` - Issues assigned to Copilot
- `copilot` - PRs created by automated systems
- `automated` - Automated actions
- `in-progress` - Work currently being done
- `completed` - Finished tasks
- `learning` - Insights and learnings
- `progress-report` - Progress tracking issues

## Scheduled Workflows

The autonomous system runs on these schedules:
- **Idea Generator**: Daily at 9 AM UTC
- **Auto Review & Merge**: Every 2 hours
- **Issue to PR**: Every 3 hours
- **Auto Close Issues**: Every 4 hours
- **Timeline Updater**: Every 6 hours
- **Progress Tracker**: Every 12 hours

All workflows can also be triggered manually via the Actions tab.

## Optional: Custom Domain

To use a custom domain for GitHub Pages:
1. Add a CNAME file in the docs/ directory
2. Configure DNS settings with your domain provider
3. Update the domain in Repository Settings → Pages

## Security Considerations

This repository is designed for experimentation and entertainment. For production use:
- Add required status checks before merge
- Implement comprehensive testing
- Add code scanning and security analysis
- Consider limiting auto-merge to specific branches
- Review automated changes periodically
