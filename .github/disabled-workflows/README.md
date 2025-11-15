# Disabled Workflows

This directory contains GitHub Actions workflow files that have been intentionally disabled but preserved for future reference.

## Why are workflows moved here?

GitHub Actions validates all `.yml` files in `.github/workflows/`, even if their triggers are commented out. This causes validation errors. Moving disabled workflows to this directory:

1. ✅ Removes the validation error from GitHub Actions
2. ✅ Preserves the workflow code for future reference
3. ✅ Makes it clear which workflows are intentionally disabled
4. ✅ Allows easy re-enabling by moving back to `.github/workflows/`

## How to re-enable a workflow

To re-enable a workflow from this directory:

1. Move the workflow file back to `.github/workflows/`
2. Uncomment any commented-out trigger sections (the `on:` section)
3. Commit and push the changes

## Currently Disabled Workflows

- **suggest-collaborations.yml** - Disabled 2025-11-15. Agent collaboration suggestion system. Can be re-enabled by uncommenting the `on:` section and moving back to workflows directory.
