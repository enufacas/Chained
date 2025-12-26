# ADK A2A Blog Pipeline - Issue Comments Templates

This directory contains template comments for the ADK A2A Blog Pipeline tracking issue system.

## Purpose

These templates provide standardized, comprehensive comments that can be posted to tracking issues to explain the system and provide helpful information to users.

## Available Templates

### ADK_PIPELINE_TRACKING_WELCOME.md (✨ NEW - Recommended)

**Use Case:** Complete initialization of new tracking issues

**Contents:**
- System status with all component verification
- Comprehensive "How it works" explanation
- Quick commands for all common operations
- A2A pipeline architecture diagram
- Documentation links (quick start, guides, technical details)
- Pipeline schedule
- Expected comment format examples
- Monitoring & diagnostics commands
- Infrastructure design principles
- About @create-botter section
- Full operational status footer

**When to Use:**
- When initializing any new tracking issue (primary use case)
- After major infrastructure updates
- For onboarding new team members
- To provide complete system overview

**Script:** `tools/post-adk-tracking-welcome.sh` - Automated posting script

### ADK_PIPELINE_INITIAL_STATUS.md

**Use Case:** First-time setup of a tracking issue (Legacy - use TRACKING_WELCOME instead)

**Contents:**
- Purpose and overview of tracking system
- How the system works
- Quick reference commands
- Pipeline architecture diagram
- System components table
- Execution modes explanation
- Configuration details
- Helper script commands
- Monitoring instructions
- Expected comment format
- Infrastructure status
- Documentation links
- Design philosophy
- Getting help section
- Success metrics

**When to Use:**
- Legacy template - consider using ADK_PIPELINE_TRACKING_WELCOME.md instead
- When creating a new tracking issue
- After significant system updates
- For onboarding new team members
- To refresh stale tracking issues

### ADK_PIPELINE_STATUS_COMMENT.md

**Use Case:** Status updates and verification comments

**Contents:**
- Status update header
- Infrastructure status table
- How tracking works
- Quick commands
- A2A architecture diagram
- Documentation links
- Pipeline schedule
- What to expect
- Infrastructure design principles
- Ready for production message

**When to Use:**
- After verifying system health
- Following infrastructure updates
- As periodic status check-ins
- To confirm operational status

## Usage

### Manual Posting

**Post initial status comment:**
```bash
ISSUE_NUMBER=194  # Replace with actual issue number
gh issue comment "$ISSUE_NUMBER" --body-file docs/issue-comments/ADK_PIPELINE_INITIAL_STATUS.md
```

**Post status update:**
```bash
gh issue comment "$ISSUE_NUMBER" --body-file docs/issue-comments/ADK_PIPELINE_STATUS_COMMENT.md
```

### Via Script (Recommended)

**Preferred method** - Use the dedicated welcome posting script:

```bash
# Auto-detect tracking issue and post welcome comment
./tools/post-adk-tracking-welcome.sh

# Or specify issue number
./tools/post-adk-tracking-welcome.sh 4069
```

**Legacy method** - The `tools/initialize-adk-tracking-issue.sh` script automatically generates and posts a welcome comment:

```bash
# Auto-detect tracking issue and initialize (legacy)
./tools/initialize-adk-tracking-issue.sh

# Or specify issue number
./tools/initialize-adk-tracking-issue.sh 194
```

## Customization

### Adding New Templates

1. Create new `.md` file in this directory
2. Use existing templates as structure guide
3. Include relevant sections:
   - Clear header/title
   - Purpose statement
   - Actionable information
   - Documentation links
   - Attribution footer
4. Update this README with template description

### Template Guidelines

**Do ✅**
- Use clear, concise language
- Include actionable commands
- Provide documentation links
- Use emojis for visual organization
- Add timestamps/dates
- Include @create-botter attribution

**Don't ❌**
- Include outdated information
- Use hardcoded issue numbers
- Skip documentation links
- Omit command examples
- Forget attribution

## Template Structure

### Standard Sections

Most templates should include:

1. **Header** - Title and purpose
2. **Status** - Current operational status
3. **Overview** - What the system does
4. **Quick Commands** - Copy-paste ready commands
5. **Architecture** - Visual diagrams
6. **Documentation** - Links to guides
7. **Schedule** - When things run
8. **Help** - Where to get support
9. **Footer** - Attribution and dates

### Markdown Formatting

**Use consistent formatting:**
- Headers: `##`, `###`, `####`
- Tables: For status, components, schedules
- Code blocks: With language tags
- Lists: Bulleted or numbered
- Emojis: For visual landmarks
- Links: To documentation and code

## Maintenance

### Regular Updates

**When to update templates:**
- Workflow schedule changes
- New helper commands added
- Documentation links change
- System architecture updates
- New features added

**How to update:**
1. Edit template file
2. Test with dry run posting
3. Update this README if structure changes
4. Commit changes with descriptive message

### Version Control

Templates are version controlled in git:
- Track changes over time
- Review template evolution
- Rollback if needed
- Share across forks

## Related Files

**Scripts:**
- `../../tools/post-adk-tracking-welcome.sh` - Posts ADK_PIPELINE_TRACKING_WELCOME.md (recommended)
- `../../tools/initialize-adk-tracking-issue.sh` - Legacy initialization script
- `../../tools/adk-pipeline-status.sh` - Helper commands referenced in templates

**Documentation:**
- `../ADK_PIPELINE_TRACKING_SETUP.md` - Complete setup guide
- `../ADK_PIPELINE_STATUS_GUIDE.md` - Status monitoring guide
- `../ADK_PIPELINE_QUICK_REF.md` - Quick reference
- `../ADK_PIPELINE_TRACKING_GUIDE.md` - Tracking system guide

**Workflow:**
- `../../.github/workflows/adk-a2a-blog-pipeline.yml` - Posts automated comments

**Tests:**
- `../../tests/test_adk_blog_pipeline.py` - Tests infrastructure

## Examples

### Example: Posting Initial Setup Comment

```bash
#!/bin/bash
# Find tracking issue by label
ISSUE_NUMBER=$(gh issue list --label "adk-pipeline" --state open --limit 1 --json number --jq '.[0].number')

if [[ -n "$ISSUE_NUMBER" ]]; then
    echo "Posting initial status to issue #$ISSUE_NUMBER..."
    gh issue comment "$ISSUE_NUMBER" --body-file docs/issue-comments/ADK_PIPELINE_INITIAL_STATUS.md
    echo "✅ Comment posted successfully"
else
    echo "❌ No tracking issue found with label 'adk-pipeline'"
fi
```

### Example: Posting Status Update

```bash
#!/bin/bash
# Post status update to specific issue
ISSUE_NUMBER=194

echo "Posting status update to issue #$ISSUE_NUMBER..."
gh issue comment "$ISSUE_NUMBER" --body-file docs/issue-comments/ADK_PIPELINE_STATUS_COMMENT.md
echo "✅ Status update posted"
```

## Best Practices

### Content Best Practices

1. **Be Concise** - Provide essential information without overwhelming
2. **Be Actionable** - Include commands users can run immediately
3. **Be Current** - Keep templates updated with latest info
4. **Be Helpful** - Link to relevant documentation
5. **Be Consistent** - Use standard formatting and structure

### Usage Best Practices

1. **Test First** - Preview templates before posting to issues
2. **Update Regularly** - Keep templates in sync with system changes
3. **Document Changes** - Note what changed and why
4. **Review Old Posts** - Ensure historical comments still make sense
5. **Archive Outdated** - Move old templates to archive/ subdirectory

## Troubleshooting

### Template Not Rendering

**Problem:** Markdown not rendering correctly in GitHub

**Solutions:**
- Check for malformed tables
- Verify code block syntax
- Ensure emoji codes are valid
- Test in GitHub markdown preview

### Links Not Working

**Problem:** Documentation links broken

**Solutions:**
- Use relative paths for in-repo links
- Verify file paths are correct
- Test links after posting
- Update broken links promptly

### Commands Not Working

**Problem:** Example commands fail when run

**Solutions:**
- Test all commands before committing
- Include prerequisites (gh CLI, gcloud, etc.)
- Provide clear error messages
- Update commands if tools change

## Contributing

### Adding New Templates

1. Create template in this directory
2. Follow existing structure
3. Test template by posting to test issue
4. Update this README
5. Create PR with changes

### Improving Existing Templates

1. Identify improvement needed
2. Update template file
3. Test changes
4. Update README if structure changed
5. Create PR with clear description

---

**📝 Templates by @create-botter** - _Creating documentation that illuminates understanding._

**Directory Version:** 1.1  
**Last Updated:** 2025-12-26  
**Template Count:** 3 active templates (1 new, 2 legacy)  
**Recommended:** Use `ADK_PIPELINE_TRACKING_WELCOME.md` + `post-adk-tracking-welcome.sh`
