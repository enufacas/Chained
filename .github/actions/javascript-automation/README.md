# JavaScript/TypeScript Project Automation Action

**Created by @create-botter** - Visionary automation inspired by Nikola Tesla ⚡

## Overview

This composite action provides comprehensive automation for JavaScript and TypeScript projects, including Next.js, React, Playwright, and generic Node.js applications. It automatically detects your project type, package manager, and provides intelligent defaults while allowing full customization.

## Features

- 🔍 **Smart Detection**: Auto-detects project type (Next.js, React, Playwright, generic)
- 📦 **Multi-Package Manager**: Supports npm, yarn, and pnpm with automatic detection
- 🎯 **TypeScript Support**: Detects and handles TypeScript projects
- ⚙️ **Configurable Workflow**: Enable/disable specific steps (install, build, lint, test)
- 🔧 **Custom Commands**: Override default commands for build, lint, and test
- 📊 **Detailed Outputs**: Reports status of each step for downstream use
- 🎨 **Beautiful Logging**: Clear, emoji-enhanced console output

## Usage

### Basic Usage (Auto-detect everything)

```yaml
- name: Checkout code
  uses: actions/checkout@v4

- name: Run JavaScript automation
  uses: ./.github/actions/javascript-automation
  with:
    node-version: '18'
```

This will:
1. Detect package manager (npm/yarn/pnpm) from lock files
2. Detect project type (Next.js, React, Playwright, etc.)
3. Install dependencies
4. Run build (if build script exists)
5. Run lint (if lint script exists)
6. Run tests (if test script exists)

### Next.js Project

```yaml
- name: Build and test Next.js app
  uses: ./.github/actions/javascript-automation
  with:
    working-directory: 'frontend'
    node-version: '18'
    run-build: 'true'
    run-lint: 'true'
    run-tests: 'true'
```

### Playwright Test Suite

```yaml
- name: Run Playwright tests
  uses: ./.github/actions/javascript-automation
  with:
    working-directory: 'tests/e2e'
    run-build: 'false'
    run-lint: 'false'
    test-command: 'npx playwright test --grep @smoke'
```

### Custom Build Process

```yaml
- name: Custom build workflow
  uses: ./.github/actions/javascript-automation
  with:
    node-version: '20'
    package-manager: 'pnpm'
    build-command: 'pnpm run build:production'
    lint-command: 'pnpm run lint:strict'
    test-command: 'pnpm run test:coverage'
```

### Lint Only

```yaml
- name: Run linter only
  uses: ./.github/actions/javascript-automation
  with:
    run-build: 'false'
    run-tests: 'false'
    run-lint: 'true'
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `node-version` | Node.js version to use | No | `'18'` |
| `package-manager` | Package manager (npm/yarn/pnpm) | No | `'npm'` (auto-detected) |
| `install-dependencies` | Whether to install dependencies | No | `'true'` |
| `run-build` | Whether to run build command | No | `'true'` |
| `run-lint` | Whether to run linting | No | `'true'` |
| `run-tests` | Whether to run tests | No | `'true'` |
| `working-directory` | Working directory for the project | No | `'.'` |
| `build-command` | Custom build command (overrides default) | No | `''` |
| `test-command` | Custom test command (overrides default) | No | `''` |
| `lint-command` | Custom lint command (overrides default) | No | `''` |

## Outputs

| Output | Description |
|--------|-------------|
| `build-status` | Build status: `success`, `skipped`, or `failed` |
| `test-status` | Test status: `success`, `skipped`, or `failed` |
| `lint-status` | Lint status: `success`, `skipped`, or `failed` |

### Using Outputs

```yaml
- name: Run automation
  id: js-automation
  uses: ./.github/actions/javascript-automation

- name: Check build result
  if: steps.js-automation.outputs.build-status == 'failed'
  run: echo "Build failed!"

- name: Check all passed
  if: |
    steps.js-automation.outputs.build-status == 'success' &&
    steps.js-automation.outputs.test-status == 'success' &&
    steps.js-automation.outputs.lint-status == 'success'
  run: echo "All checks passed!"
```

## Auto-Detection Details

### Package Manager Detection

The action detects package manager in this order:
1. If `pnpm-lock.yaml` exists → uses `pnpm`
2. If `yarn.lock` exists → uses `yarn`
3. If `package-lock.json` exists or neither → uses `npm`
4. Can be overridden with `package-manager` input

### Project Type Detection

Detected from `package.json` dependencies:
- **Next.js**: Contains `"next"` dependency
- **Playwright**: Contains `"@playwright/test"` dependency
- **React**: Contains `"react"` dependency
- **Generic**: Fallback for other Node.js projects

### TypeScript Detection

Detected if `package.json` contains `"typescript"` dependency.

## Command Defaults

If custom commands are not provided, the action auto-detects from `package.json`:

### Build
- Looks for `"build"` script in `package.json`
- Executes `npm run build` / `yarn build` / `pnpm build`
- Skips if no build script exists

### Lint
- Looks for `"lint"` script in `package.json`
- Executes `npm run lint` / `yarn lint` / `pnpm lint`
- Skips if no lint script exists

### Test
- Looks for `"test"` script in `package.json`
- Executes `npm test` / `yarn test` / `pnpm test`
- Skips if no test script exists

## Real-World Examples

### Monorepo with Multiple Projects

```yaml
jobs:
  ui-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build UI frontend
        uses: ./.github/actions/javascript-automation
        with:
          working-directory: 'packages/ui-frontend'
          node-version: '18'
  
  admin-dashboard:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build admin dashboard
        uses: ./.github/actions/javascript-automation
        with:
          working-directory: 'packages/admin-dashboard'
          package-manager: 'pnpm'
```

### CI/CD Pipeline with Deploy

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Test application
        id: test
        uses: ./.github/actions/javascript-automation
        with:
          run-build: 'false'
          run-tests: 'true'
          run-lint: 'true'
  
  build-deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build for production
        uses: ./.github/actions/javascript-automation
        with:
          build-command: 'npm run build:production'
          run-tests: 'false'
          run-lint: 'false'
      
      - name: Deploy to production
        run: npm run deploy
```

## Troubleshooting

### Build Fails

- Check that `package.json` contains a `"build"` script
- Verify dependencies are correctly specified in `package.json`
- Try running locally: `npm run build` (or yarn/pnpm)

### Tests Fail

- Ensure test script exists in `package.json`
- Check test configuration files are present
- Verify test dependencies are installed

### Package Manager Not Detected

- Ensure lock file exists (`package-lock.json`, `yarn.lock`, or `pnpm-lock.yaml`)
- Or explicitly specify with `package-manager` input

## Integration with Other Actions

### With Python Automation

```yaml
- name: Python backend tests
  uses: ./.github/actions/python-automation
  with:
    python-version: '3.11'

- name: JavaScript frontend tests
  uses: ./.github/actions/javascript-automation
  with:
    working-directory: 'frontend'
```

### With Custom Actions

```yaml
- name: Install dependencies
  uses: ./.github/actions/npm-commands
  with:
    command: 'install'

- name: Build and test
  uses: ./.github/actions/javascript-automation
  with:
    install-dependencies: 'false'  # Already installed above
```

## Design Philosophy

Following the visionary spirit of **@create-botter**, this action embodies:

- **Intelligent Automation**: Smart detection reduces configuration burden
- **Flexibility**: Comprehensive options for customization when needed
- **Clarity**: Clear outputs and beautiful logging
- **Reliability**: Robust error handling and validation
- **Elegance**: One action, many use cases

---

*Created by @create-botter - Visionary infrastructure inspired by Nikola Tesla* ⚡  
*Part of the Chained autonomous AI ecosystem - Infrastructure that illuminates possibilities*
