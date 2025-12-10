---
applyTo:
  - "infrastructure/docker/ag-ui-frontend/**"
  - "infrastructure/docker/ag-organism-frontend/**"
  - "**/package.json"
---

# NPM Package Management Requirements

## CRITICAL: Always Regenerate package-lock.json

When modifying `package.json` in ANY project, you **MUST** regenerate the `package-lock.json` file before committing. This is **not optional**.

### Why This Matters

- **Docker builds fail**: `npm ci` requires package.json and package-lock.json to be in perfect sync
- **CI/CD breaks**: Deployment workflows will fail with cryptic "Missing from lock file" errors
- **Recurring issue**: This has caused multiple build failures (see commits #3785, #3490, #3433, and now #20086950265)

### Required Workflow

**EVERY TIME** you add, remove, or update a dependency in package.json:

```bash
# 1. Delete the old lock file
rm package-lock.json

# 2. Regenerate with npm install
npm install

# 3. Verify the lock file was created
ls -lh package-lock.json

# 4. Test that npm ci works
npm ci

# 5. Commit BOTH files together
git add package.json package-lock.json
git commit -m "fix: Update dependencies and regenerate lock file"
```

### Common Scenarios

#### Adding a New Dependency

```bash
# ❌ WRONG - Don't do this:
# Edit package.json manually
# git add package.json
# git commit

# ✅ CORRECT - Do this:
npm install new-package@version
git add package.json package-lock.json
git commit -m "feat: Add new-package dependency"
```

#### Updating Dependencies

```bash
# ❌ WRONG:
# Edit package.json version number
# git commit

# ✅ CORRECT:
npm install package@new-version
# OR for multiple updates:
npm update
git add package.json package-lock.json
git commit -m "chore: Update dependencies"
```

#### After Merge Conflicts

```bash
# After resolving package.json conflicts:
rm package-lock.json
npm install
git add package-lock.json
git commit -m "fix: Regenerate lock file after merge"
```

### Validation Checklist

Before creating a PR that modifies package.json:

- [ ] package-lock.json exists and is up-to-date
- [ ] `npm ci` runs successfully without errors
- [ ] Docker build completes (if applicable): `docker build -t test .`
- [ ] Both package.json and package-lock.json are committed together
- [ ] No "Missing from lock file" errors in the commit

### Detecting Sync Issues

If you see these errors, the lock file is out of sync:

```
npm error `npm ci` can only install packages when your package.json 
and package-lock.json or npm-shrinkwrap.json are in sync.

npm error Missing: <package-name>@<version> from lock file
npm error Invalid: lock file's <package> does not satisfy <package>
```

**Solution**: Delete package-lock.json and run `npm install`

### Why npm ci Instead of npm install?

- **npm ci**: Clean install from lock file (used in CI/CD, Docker)
  - Requires lock file to be in perfect sync
  - Faster and more reliable for automated builds
  - Deletes node_modules and installs from scratch

- **npm install**: Updates lock file based on package.json
  - More forgiving but less deterministic
  - Should be used in development
  - Updates the lock file automatically

### Docker Build Context

The Dockerfile uses `npm ci` because:

1. **Reproducibility**: Ensures exact same dependencies every time
2. **Speed**: Faster in containerized environments
3. **Reliability**: Fails fast if files are out of sync (catches errors early)

Example from Dockerfile:
```dockerfile
COPY package.json package-lock.json* ./
RUN npm ci  # This WILL FAIL if lock file is out of sync
```

### Historical Context

This issue has occurred multiple times:

- **2024-12-10**: Added three.js dependencies without updating lock file ([Run #20086950265](https://github.com/enufacas/Chained/actions/runs/20086950265))
- **Previous**: Added Firestore dependencies (#3785)
- **Previous**: Added @testing-library dependencies (#3490)
- **Previous**: Multiple other occurrences (#3433)

### Prevention

To prevent this issue:

1. **Always use npm install** when modifying dependencies
2. **Never edit package.json manually** without regenerating the lock file
3. **Test npm ci locally** before pushing
4. **Check CI logs** for "Missing from lock file" errors
5. **Use this instruction file** as a reference

### Related Instructions

- `.github/instructions/a2a-ui-development.instructions.md` - Testing checklist includes npm commands
- `.github/instructions/branch-protection.instructions.md` - PR requirements

---

**Remember**: package.json and package-lock.json are a **pair**. They must always be updated together.
