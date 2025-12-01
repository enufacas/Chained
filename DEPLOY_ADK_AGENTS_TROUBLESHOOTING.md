# Deploy ADK Agents Workflow Troubleshooting

## Investigation Summary

**Date**: December 1, 2025  
**Workflow**: `.github/workflows/deploy-adk-agents.yml`  
**Issue Reported**: "max cpu count or something similar"

## Findings

### Most Recent Failure (Dec 1, 2025 at 14:46:45Z)

**Run ID**: 19826648953  
**Job Failed**: "Build AG-UI Frontend" (Job ID: 56801665930)

**Actual Error**: npm ci sync error (NOT "max cpu count")

```
npm error `npm ci` can only install packages when your package.json and 
package-lock.json or npm-shrinkwrap.json are in sync. Please update your 
lock file with `npm install` before continuing.

npm error Missing: @browserbasehq/stagehand@1.14.0 from lock file
npm error Missing: dotenv@16.6.1 from lock file
npm error Missing: @playwright/test@1.57.0 from lock file
... (50+ missing dependencies)
```

### Root Cause

The `infrastructure/docker/ag-ui-frontend/package-lock.json` file was out of sync with `package.json`. When dependencies were added to `package.json`, the lock file was not regenerated with `npm install`.

### Resolution

**Fixed in commits**:
- `95af796e` - "fix: Regenerate package-lock.json for AG-UI frontend to fix npm ci build failure"
- `5cc3ade6` - "Fix npm ci failure in AG-UI Frontend Docker build (#3490)"

**Current Status**: ✅ **RESOLVED** - Subsequent workflow runs have succeeded (verified runs after Dec 1 at 14:46:45Z)

### Verification

```bash
cd infrastructure/docker/ag-ui-frontend
npm ci --dry-run
# Result: Success - package-lock.json is now in sync
```

## CPU Configuration Analysis

**Searched for "max cpu count" errors**: None found in recent workflow runs.

**CPU Configuration in Terraform** (`infrastructure/terraform/adk-agents.tf`):
- All Cloud Run services configured with `cpu = "1"`
- This is a valid and standard configuration
- No CPU-related errors in workflow logs

**Hypothesis**: The user may have:
1. Confused the npm ci error with a CPU error
2. Remembered a different workflow failure
3. Referred to an older failure not in recent history

## Recommendations

### For Future Development

1. **Always regenerate package-lock.json** when modifying package.json:
   ```bash
   cd infrastructure/docker/ag-ui-frontend
   npm install
   git add package.json package-lock.json
   git commit -m "chore: update dependencies"
   ```

2. **Consider adding a pre-commit hook** to validate package-lock.json sync:
   ```bash
   #!/bin/bash
   cd infrastructure/docker/ag-ui-frontend
   npm ci --dry-run || {
     echo "ERROR: package-lock.json out of sync"
     echo "Run: npm install"
     exit 1
   }
   ```

3. **Add workflow validation step** (optional):
   ```yaml
   - name: Validate npm dependencies
     run: |
       cd infrastructure/docker/ag-ui-frontend
       npm ci --dry-run
   ```

## Related Workflows

Other workflows that may have similar dependency sync issues:
- `.github/workflows/adk-a2a-blog-pipeline.yml`
- Any workflow building Node.js Docker containers

## Additional Notes

- The workflow has multiple build jobs running in parallel (matrix strategy)
- Only the AG-UI Frontend build failed; other agent builds succeeded
- The fix was straightforward: regenerate package-lock.json with npm install
- No changes to CPU configuration were needed or made

## Conclusion

The deploy-adk-agents workflow failed due to an npm dependency synchronization issue, not a CPU configuration problem. The issue was identified and resolved on December 1, 2025. The workflow is currently functioning correctly.

---

**Troubleshooting by**: @troubleshoot-expert  
**Generated**: December 1, 2025
