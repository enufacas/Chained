# NPM Command Runner Action

**Created by @create-botter** - Visionary automation inspired by Nikola Tesla ⚡

## Overview

A flexible, reusable action for running any npm/yarn/pnpm command with automatic package manager detection, comprehensive error handling, and output capture capabilities.

## Features

- 🎯 **Universal Runner**: Execute any npm/yarn/pnpm command
- 🔍 **Auto-Detection**: Automatically detects package manager from lock files
- 📦 **Multi-Manager Support**: Works seamlessly with npm, yarn, and pnpm
- 📝 **Output Capture**: Optionally save command output to file
- ⚙️ **Flexible Error Handling**: Configurable failure behavior
- 📊 **Detailed Outputs**: Reports exit code and command output

## Quick Start

```yaml
- name: Install dependencies
  uses: ./.github/actions/npm-commands
  with:
    command: 'install'

- name: Run tests
  uses: ./.github/actions/npm-commands
  with:
    command: 'test'

- name: Build project
  uses: ./.github/actions/npm-commands
  with:
    command: 'run'
    args: 'build'
```

## Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `command` | NPM command to run (install, run, test, build, publish, etc.) | Yes | - |
| `args` | Additional arguments for the command | No | `''` |
| `working-directory` | Working directory for the command | No | `'.'` |
| `package-manager` | Package manager (npm/yarn/pnpm/auto) | No | `'auto'` |
| `node-version` | Node.js version (empty to skip setup) | No | `'18'` |
| `fail-on-error` | Whether to fail action if command fails | No | `'true'` |
| `output-file` | File to save command output to | No | `''` |

## Outputs

| Output | Description |
|--------|-------------|
| `exit-code` | Exit code of the command |
| `output` | Output from the command (multiline-safe) |
| `package-manager-used` | Package manager that was used |

## Usage Examples

### Install Dependencies

```yaml
# Auto-detect package manager
- name: Install dependencies
  uses: ./.github/actions/npm-commands
  with:
    command: 'install'

# Force specific package manager
- name: Install with pnpm
  uses: ./.github/actions/npm-commands
  with:
    command: 'install'
    package-manager: 'pnpm'
```

### Run Scripts

```yaml
- name: Run build script
  uses: ./.github/actions/npm-commands
  with:
    command: 'run'
    args: 'build'

- name: Run dev server
  uses: ./.github/actions/npm-commands
  with:
    command: 'run'
    args: 'dev'
```

### Run Tests

```yaml
- name: Run tests
  uses: ./.github/actions/npm-commands
  with:
    command: 'test'

- name: Run tests with coverage
  uses: ./.github/actions/npm-commands
  with:
    command: 'test'
    args: '--coverage --verbose'
```

### Publish Package

```yaml
- name: Publish to npm
  uses: ./.github/actions/npm-commands
  with:
    command: 'publish'
    args: '--access public'
```

### Custom npm Commands

```yaml
- name: View package info
  uses: ./.github/actions/npm-commands
  with:
    command: 'view'
    args: 'lodash version'

- name: Check outdated packages
  uses: ./.github/actions/npm-commands
  with:
    command: 'outdated'
    fail-on-error: 'false'
```

### With Output Capture

```yaml
- name: Run tests and save output
  uses: ./.github/actions/npm-commands
  with:
    command: 'test'
    args: '--json'
    output-file: 'test-results.json'

- name: Upload test results
  uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: test-results.json
```

### Multiple Package.json Projects

```yaml
- name: Build frontend
  uses: ./.github/actions/npm-commands
  with:
    command: 'run'
    args: 'build'
    working-directory: 'frontend'

- name: Build backend
  uses: ./.github/actions/npm-commands
  with:
    command: 'run'
    args: 'build'
    working-directory: 'backend'
```

### Skip Node Setup

```yaml
# If Node.js is already set up
- name: Run command without Node setup
  uses: ./.github/actions/npm-commands
  with:
    command: 'test'
    node-version: ''  # Skip Node.js setup
```

### Using Outputs

```yaml
- name: Run tests
  id: test
  uses: ./.github/actions/npm-commands
  with:
    command: 'test'
    fail-on-error: 'false'

- name: Check test result
  run: |
    if [ "${{ steps.test.outputs.exit-code }}" != "0" ]; then
      echo "Tests failed!"
      echo "Output: ${{ steps.test.outputs.output }}"
    fi

- name: Report package manager
  run: |
    echo "Used: ${{ steps.test.outputs.package-manager-used }}"
```

## Package Manager Auto-Detection

The action detects the package manager in this priority order:

1. If `package-manager` input is set to npm/yarn/pnpm → uses that
2. If `pnpm-lock.yaml` exists → uses pnpm
3. If `yarn.lock` exists → uses yarn
4. If `package-lock.json` exists → uses npm
5. Otherwise → defaults to npm

## Command Translation

The action intelligently translates commands for different package managers:

### npm
- `install` → `npm install`
- `run <script>` → `npm run <script>`
- `test` → `npm test`
- `build` → `npm run build`

### yarn
- `install` → `yarn install`
- `run <script>` → `yarn <script>` (no 'run' needed)
- `test` → `yarn test`
- `build` → `yarn build`

### pnpm
- `install` → `pnpm install`
- `run <script>` → `pnpm run <script>`
- `test` → `pnpm test`
- `build` → `pnpm build`

## Error Handling

### Fail on Error (Default)

```yaml
- name: Install dependencies
  uses: ./.github/actions/npm-commands
  with:
    command: 'install'
    fail-on-error: 'true'  # Action will fail if command fails
```

### Continue on Error

```yaml
- name: Check for security issues
  uses: ./.github/actions/npm-commands
  with:
    command: 'audit'
    fail-on-error: 'false'  # Action continues even if audit finds issues

- name: Continue workflow
  run: echo "Continuing despite audit results"
```

## Real-World Examples

### Complete CI Pipeline

```yaml
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install dependencies
        uses: ./.github/actions/npm-commands
        with:
          command: 'install'
      
      - name: Run linter
        uses: ./.github/actions/npm-commands
        with:
          command: 'run'
          args: 'lint'
      
      - name: Run tests
        uses: ./.github/actions/npm-commands
        with:
          command: 'test'
          args: '--coverage'
      
      - name: Build
        uses: ./.github/actions/npm-commands
        with:
          command: 'run'
          args: 'build'
```

### Monorepo Workflow

```yaml
jobs:
  build-packages:
    strategy:
      matrix:
        package: [frontend, backend, shared]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install dependencies for ${{ matrix.package }}
        uses: ./.github/actions/npm-commands
        with:
          command: 'install'
          working-directory: 'packages/${{ matrix.package }}'
      
      - name: Build ${{ matrix.package }}
        uses: ./.github/actions/npm-commands
        with:
          command: 'run'
          args: 'build'
          working-directory: 'packages/${{ matrix.package }}'
```

### Conditional Publishing

```yaml
- name: Run tests
  id: test
  uses: ./.github/actions/npm-commands
  with:
    command: 'test'

- name: Publish if tests pass
  if: steps.test.outputs.exit-code == '0' && github.ref == 'refs/heads/main'
  uses: ./.github/actions/npm-commands
  with:
    command: 'publish'
    args: '--access public'
```

### Debug Mode

```yaml
- name: Run command with full output
  uses: ./.github/actions/npm-commands
  with:
    command: 'run'
    args: 'build --verbose'
    output-file: 'build-log.txt'

- name: Show build log
  if: failure()
  run: cat build-log.txt
```

## Integration with Other Actions

### With JavaScript Automation

```yaml
# Install once, then run automation
- name: Install dependencies
  uses: ./.github/actions/npm-commands
  with:
    command: 'install'

- name: Build and test
  uses: ./.github/actions/javascript-automation
  with:
    install-dependencies: 'false'  # Skip install
```

### With Custom Deployment

```yaml
- name: Build for production
  uses: ./.github/actions/npm-commands
  with:
    command: 'run'
    args: 'build:production'

- name: Deploy
  uses: ./.github/actions/npm-commands
  with:
    command: 'run'
    args: 'deploy'
```

## Troubleshooting

### Command Not Found

Ensure the script exists in `package.json`:
```json
{
  "scripts": {
    "build": "next build",
    "test": "jest"
  }
}
```

### Package Manager Not Detected

- Check for lock files in working directory
- Or explicitly set `package-manager` input

### Exit Code Issues

Use `fail-on-error: 'false'` and check `exit-code` output for custom handling.

## Design Philosophy

Following the visionary spirit of **@create-botter**, this action embodies:

- **Universality**: One action for all npm commands
- **Intelligence**: Smart package manager detection
- **Flexibility**: Configurable for any use case
- **Clarity**: Clear outputs and error messages
- **Simplicity**: Minimal configuration, maximum capability

---

*Created by @create-botter - Visionary infrastructure inspired by Nikola Tesla* ⚡  
*Part of the Chained autonomous AI ecosystem - Infrastructure that illuminates possibilities*
