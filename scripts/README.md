# Utility Scripts

This directory contains shell scripts and utility programs for managing and monitoring the Chained system.

## Scripts

### System Management
- **`kickoff-system.sh`** - Initialize and start the Chained autonomous system
- **`validate-system.sh`** - Run validation checks on the system configuration
- **`validate-consolidation.sh`** - Validate workflow consolidation

### Monitoring & Status
- **`check-status.sh`** - Check overall system health and status
- **`verify-schedules.sh`** - Verify scheduled workflow health
- **`evaluate-workflows.sh`** - Evaluate workflow performance and health

### Data Management
- **`manual-data-refresh.sh`** - Manually refresh system data

### Repository Setup
- **`create-missing-labels.sh`** - Create missing repository labels required by automated workflows
- **`fix-workflow-labels.sh`** - 🔧 **NEW** Quick fix for workflow label issues (by @troubleshoot-expert)

### Demonstrations
- **`demo-archaeology-learning.sh`** - Demonstrate archaeology learning features
- **`demo-time-travel.py`** - Python script demonstrating time-travel debugging features

## Usage

All scripts should be run from the repository root:

```bash
# Check system status
./scripts/check-status.sh

# Validate system configuration
./scripts/validate-system.sh

# Initialize the system (typically run once)
./scripts/kickoff-system.sh
```

## Prerequisites

Most scripts require:
- Bash shell
- GitHub CLI (`gh`) for GitHub interactions
- Python 3 for Python scripts
- Appropriate permissions and GitHub tokens

## Documentation

For more details on specific scripts, see:
- [System Documentation](../docs/)
- [Getting Started Guide](../GETTING_STARTED.md)
- [Monitoring Guide](../docs/MONITORING.md)
- **[Workflow Troubleshooting Guide](../.github/workflows/TROUBLESHOOTING.md)** - 🔧 **NEW** by @troubleshoot-expert

## Troubleshooting

If workflows are failing with label-related errors:

1. **Quick Fix:**
   ```bash
   bash scripts/fix-workflow-labels.sh
   ```

2. **Or manually:**
   ```bash
   python3 tools/create_labels.py --all
   ```

3. **Or via GitHub Actions:**
   - Go to Actions → "Maintenance: Ensure Repository Labels Exist"
   - Click "Run workflow"

See `.github/workflows/TROUBLESHOOTING.md` for comprehensive troubleshooting guidance.
