---
applyTo:
  - "/*.md"
  - "/*.txt"
  - "/*.json"
  - "/*.sh"
  - "/*.py"
---

# Root Directory Protection

## CRITICAL: Root Directory Has Strict File Policies

**Do NOT create arbitrary files in the repository root.** Follow the placement rules below.

## Files ALLOWED in Root

### Documentation (Core Only)
- `README.md`, `LICENSE`, `FAQ.md`
- `GETTING_STARTED.md`, `QUICKSTART.md`, `CONFIGURATION.md`
- `CONTRIBUTING.md`, `CHANGELOG.md`, `SECURITY.md`

### System Configuration
- `.gitignore`, `.copilotignore`, `.copilot-instructions.md`
- `requirements.txt`, `package.json`, `pyproject.toml`
- Config files (`.prettierrc`, `eslint.config.js`, etc.)

## Files NOT Allowed in Root → Proper Locations

| File Type | Pattern | Move To |
|-----------|---------|---------|
| Implementation summaries | `*_SUMMARY.md`, `*_IMPLEMENTATION*.md` | `docs/implementation-summaries/` |
| Investigation reports | `*_ANALYSIS.md`, `*_INVESTIGATION*.md` | `docs/investigations/` |
| Fix documentation | `*_FIX.md`, `*_FIX_*.md` | `docs/investigations/` |
| Guides and tutorials | `*_GUIDE.md`, `*_HOWTO.md` | `docs/guides/` |
| Test files | `test_*.py`, `*_test.py` | `tests/` |
| Utility scripts | `*.sh`, `*.py` (tools) | `tools/` or `scripts/` |
| Data files | `*.json` (non-config) | appropriate data directory |
| Binary files | executables | `tools/bin/` or `.gitignore` |
| Log files | `*.log`, `*.txt` (logs) | `.gitignore` (don't commit) |

## Decision Tree for New Files

```
Is it a core project doc (README, LICENSE, etc.)?
├── YES → Root is OK
└── NO → Is it a config file?
    ├── YES → Root is OK
    └── NO → Is it a summary/analysis?
        ├── YES → docs/implementation-summaries/ or docs/investigations/
        └── NO → Is it a guide/tutorial?
            ├── YES → docs/guides/
            └── NO → Is it a script/tool?
                ├── YES → tools/ or scripts/
                └── NO → Is it test-related?
                    ├── YES → tests/
                    └── NO → Find appropriate subdirectory
```

## Why This Matters

- **Discoverability**: Files in proper locations are easier to find
- **Maintainability**: Organized structure reduces cognitive load
- **Automation**: Workflows expect files in standard locations
- **Cleanliness**: Root pollution obscures important files

## Before Creating Root Files

1. Check if file type belongs elsewhere (see table above)
2. If unsure, default to `docs/` subdirectory
3. NEVER commit: binaries, logs, temporary files
