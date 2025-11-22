# Publishing to NPM

**Guide created by @APIs-architect**

This guide explains how to publish the Chained Repository MCP server to npm, making it globally available via `npm install -g @chained/repository-mcp`.

## 📋 Pre-Publishing Checklist

Before publishing to npm, ensure:

- [ ] All tests pass (`npm test`)
- [ ] Build succeeds (`npm run build`)
- [ ] Version number is updated in `package.json`
- [ ] README is up-to-date with current features
- [ ] CHANGELOG is updated (if applicable)
- [ ] No sensitive data in repository
- [ ] `.npmignore` excludes dev files
- [ ] `files` field in package.json is correct

## 🔐 NPM Account Setup

### 1. Create NPM Account

If you don't have an npm account:

```bash
npm signup
```

Or visit: https://www.npmjs.com/signup

### 2. Login to NPM

```bash
npm login
```

Enter your credentials:
- Username
- Password
- Email
- 2FA code (if enabled)

### 3. Verify Login

```bash
npm whoami
```

Should display your npm username.

## 📦 Scoped Package Setup

This package uses the `@chained` scope, which requires organization access.

### Option 1: Create NPM Organization

If you own the organization:

```bash
npm org create chained
```

### Option 2: Request Access

If organization exists, request access from the owner.

### Verify Organization Access

```bash
npm access list packages @chained
```

## 🚀 Publishing Process

### 1. Prepare the Package

```bash
cd /path/to/Chained/mcp-servers/chained-repository

# Clean previous builds
rm -rf dist/
rm -rf node_modules/

# Fresh install
npm install

# Build TypeScript
npm run build

# Verify build
ls -la dist/
```

### 2. Test the Package Locally

Before publishing, test installation locally:

```bash
# Pack the package (creates a .tgz file)
npm pack

# Test global installation from the pack
npm install -g ./chained-repository-mcp-1.0.0.tgz

# Verify command works
which chained-repository-mcp
chained-repository-mcp --help 2>/dev/null || echo "Server runs in stdio mode"

# Clean up
npm uninstall -g @chained/repository-mcp
rm chained-repository-mcp-1.0.0.tgz
```

### 3. Dry Run

Test the publish process without actually publishing:

```bash
npm publish --dry-run
```

This shows:
- What files will be included
- Package size
- Any warnings or errors

### 4. Publish to NPM

**First Release (v1.0.0):**

```bash
npm publish --access public
```

**Subsequent Releases:**

```bash
# Update version first
npm version patch  # 1.0.0 -> 1.0.1
# or
npm version minor  # 1.0.1 -> 1.1.0
# or
npm version major  # 1.1.0 -> 2.0.0

# Then publish
npm publish --access public
```

### 5. Verify Publication

```bash
# Check package on npm
npm view @chained/repository-mcp

# Test installation from npm
npm install -g @chained/repository-mcp

# Verify it works
chained-repository-mcp
```

## 🔄 Updating Published Package

### Patch Version (Bug Fixes)

```bash
# Fix the bug
# Update tests
# Build

# Update version
npm version patch

# Publish
npm publish --access public
```

### Minor Version (New Features)

```bash
# Add new feature
# Update documentation
# Build

# Update version
npm version minor

# Publish
npm publish --access public
```

### Major Version (Breaking Changes)

```bash
# Make breaking changes
# Update migration guide
# Build

# Update version
npm version major

# Publish
npm publish --access public
```

## 📊 Post-Publishing Tasks

### 1. Update Repository

```bash
git add package.json package-lock.json
git commit -m "chore: publish v1.0.0 to npm"
git push
```

### 2. Create GitHub Release

```bash
git tag v1.0.0
git push origin v1.0.0

# Or use GitHub CLI
gh release create v1.0.0 \
  --title "v1.0.0 - Global MCP Availability" \
  --notes "First public release on npm"
```

### 3. Update Documentation

Update these files with npm installation instructions:
- Main README.md
- INSTALL.md
- GITHUB_COPILOT.md
- .github/actions/setup-mcp-server/README.md

### 4. Announce Release

- Update Chained documentation
- Notify agent community
- Share in relevant channels

## 🛡️ Security Best Practices

### Never Include

- Secrets or API keys
- Development credentials
- Private repository data
- User-specific configurations
- Build artifacts that aren't needed

### Always Include

- Compiled JavaScript (in `dist/`)
- Type definitions (`*.d.ts`)
- README and documentation
- License file
- Package metadata

### Before Publishing

```bash
# Check what will be published
npm pack --dry-run

# Review the .npmignore
cat .npmignore

# Verify no secrets
grep -r "secret\|password\|token" . --exclude-dir=node_modules
```

## 🐛 Troubleshooting

### "Package name too similar"

NPM may reject if similar package exists. Options:
1. Choose different scope (`@your-org/repository-mcp`)
2. Choose different name (`chained-mcp-server`)
3. Contact npm support

### "No access to @chained scope"

```bash
# Check scope access
npm access list packages @chained

# If you need to create the scope
npm org create chained
```

### "Version already exists"

```bash
# You cannot republish the same version
# Increment version
npm version patch
npm publish --access public
```

### "Authentication required"

```bash
# Login again
npm logout
npm login
```

### Build Errors

```bash
# Clean and rebuild
rm -rf dist/ node_modules/
npm install
npm run build
```

## 📈 Package Statistics

After publishing, monitor:

### Download Stats

```bash
npm view @chained/repository-mcp downloads
```

Or visit: https://www.npmjs.com/package/@chained/repository-mcp

### Package Info

```bash
npm view @chained/repository-mcp
```

### Deprecation (if needed)

```bash
# Deprecate a version
npm deprecate @chained/repository-mcp@1.0.0 "Use v1.1.0 or higher"

# Deprecate entire package (rare)
npm deprecate @chained/repository-mcp "Package moved to @new-org/new-name"
```

## 🔄 CI/CD Publishing (Optional)

For automated publishing via GitHub Actions:

**`.github/workflows/publish-npm.yml`:**
```yaml
name: Publish to NPM

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          registry-url: 'https://registry.npmjs.org'
      
      - name: Install and Build
        run: |
          cd mcp-servers/chained-repository
          npm install
          npm run build
      
      - name: Publish to NPM
        run: |
          cd mcp-servers/chained-repository
          npm publish --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

**Setup NPM Token:**
1. Generate token at: https://www.npmjs.com/settings/tokens
2. Add as GitHub secret: `NPM_TOKEN`

## 📞 Support

For publishing issues:
- **@APIs-architect** - Package maintainer
- **@investigate-champion** - Original creator
- NPM Support: https://www.npmjs.com/support

## Related Documentation

- [NPM Documentation](https://docs.npmjs.com/)
- [Publishing Scoped Packages](https://docs.npmjs.com/creating-and-publishing-scoped-public-packages)
- [Semantic Versioning](https://semver.org/)

---

**Publishing guide by @APIs-architect** 📦✨
