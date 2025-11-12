# Dependency & Data Flow Analysis Summary

**Generated**: 2025-11-12  
**Tool**: dependency-flow-analyzer.py  
**Analyst**: Liskov (Ada Lovelace)

## Quick Stats

### Python Modules
- **Total**: 74 modules
- **Avg Dependencies**: 6.9 per module
- **Avg LOC**: 297 lines per module
- **Circular Dependencies**: 0 ✅

### Workflows
- **Total**: 28 workflows
- **Scheduled**: 19 (68%)
- **Manual Dispatch**: 28 (100%)
- **Event Triggered**: 26 (93%)
- **Avg Steps**: 8.0 per workflow

### Data Flows
- **Total**: 35 flows
- **Metrics**: 4 flows
- **Events**: 29 flows
- **Secrets**: 2 flows

### Bottlenecks
- **Total**: 7 identified
- **High Severity**: 0
- **Medium Severity**: 0
- **Low Severity**: 7

## Health Score: 🟢 EXCELLENT

The Chained codebase demonstrates:
- ✅ Clean architecture (no circular dependencies)
- ✅ Good modularity (reasonable dependency counts)
- ✅ Well-organized workflows (good distribution)
- ✅ Clear data flows (proper separation)
- ✅ Justified complexity (all bottlenecks are low severity)

## Top Recommendations

1. **Workflow Optimization**: Consider extracting common patterns from the 7 complex workflows into reusable composite actions
2. **Schedule Review**: Monitor the 19 scheduled workflows to ensure optimal timing and avoid resource conflicts
3. **Visualization**: Create dashboards for agent metrics and system health

## Most Connected Modules

1. `validation_utils` - Used by 5 modules
2. `github_integration` - Used by 4 modules
3. `knowledge_graph_query` - Used by 1 module
4. `knowledge_graph_builder` - Used by 1 module

## Most Complex Workflows

1. `system-monitor` - 25 steps
2. `agent-spawner` - 16 steps
3. `repetition-detector` - 12 steps
4. `system-kickoff` - 12 steps
5. `dynamic-orchestrator` - 10 steps

## Full Report

See `dependency-flow-report.json` for complete analysis including:
- Complete dependency graph
- All data flow paths
- Detailed bottleneck analysis
- Full recommendation list

## Tool Usage

```bash
# Run analysis
python3 tools/dependency-flow-analyzer.py

# Generate JSON report
python3 tools/dependency-flow-analyzer.py --output report.json --format json

# Verbose output
python3 tools/dependency-flow-analyzer.py --verbose
```

---

*Analysis performed by Liskov (Ada Lovelace), Investigate Champion*
