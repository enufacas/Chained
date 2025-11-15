# Unsupervised Pattern Discovery Report

**Generated:** 2025-11-15T03:06:06.008381+00:00
**Total Code Elements Analyzed:** 1934
**Patterns Discovered:** 11

## Pattern Categories
- **well-documented**: 8 patterns
- **simple-function**: 2 patterns
- **anomaly**: 1 patterns

## Discovered Patterns

### 1. Well-Documented Simple Small ClassDef
- **Type:** cluster
- **Category:** well-documented
- **Occurrences:** 204
- **Confidence:** 46.45%
- **Support:** 10.55%
- **Description:** Pattern with 204 occurrences. Primarily ClassDef nodes. Average complexity: 0.1, average size: 0.5 lines. Generally well-documented. 

**Examples:**
- `tools/prompt-generator.py:31` - ClassDef
- `tools/test_semantic_similarity_engine.py:410` - ClassDef
- `tools/test_issue_discussion_learner.py:358` - ClassDef

### 2. Well-Documented Simple Small FunctionDef
- **Type:** cluster
- **Category:** well-documented
- **Occurrences:** 271
- **Confidence:** 32.14%
- **Support:** 14.01%
- **Description:** Pattern with 271 occurrences. Primarily FunctionDef nodes. Average complexity: 1.9, average size: 13.4 lines. Generally well-documented. Uses type hints. 

**Examples:**
- `tools/validate-agent-definition.py:65` - FunctionDef
- `tools/semantic_similarity_engine.py:39` - FunctionDef
- `tools/cross-repo-pattern-matcher.py:98` - FunctionDef

### 3. Well-Documented Moderate Medium FunctionDef
- **Type:** cluster
- **Category:** well-documented
- **Occurrences:** 132
- **Confidence:** 30.12%
- **Support:** 6.83%
- **Description:** Pattern with 132 occurrences. Primarily FunctionDef nodes. Average complexity: 6.2, average size: 37.4 lines. Generally well-documented. Uses type hints. Includes error handling. 

**Examples:**
- `tools/agent-metrics-collector.py:936` - FunctionDef
- `tools/creativity-metrics-analyzer.py:123` - FunctionDef
- `tools/agent-metrics-collector.py:914` - FunctionDef

### 4. Basic Simple Small Module
- **Type:** cluster
- **Category:** simple-function
- **Occurrences:** 144
- **Confidence:** 70.01%
- **Support:** 7.45%
- **Description:** Pattern with 144 occurrences. Primarily Module nodes. Average complexity: 1.0, average size: 7.0 lines. 

**Examples:**
- `tools/lazy_workflow_loader.py:0` - Module
- `tools/example_comprehensive_analysis.py:0` - Module
- `tools/example_self_documenting_ai.py:0` - Module

### 5. Basic Simple Small FunctionDef
- **Type:** cluster
- **Category:** simple-function
- **Occurrences:** 115
- **Confidence:** 37.62%
- **Support:** 5.95%
- **Description:** Pattern with 115 occurrences. Primarily FunctionDef nodes. Average complexity: 1.2, average size: 4.8 lines. 

**Examples:**
- `tools/test_api_coordination_hub.py:354` - FunctionDef
- `tools/test_api_coordination_hub.py:403` - FunctionDef
- `tools/test_lazy_workflow_evaluator.py:93` - FunctionDef

### 6. Well-Documented Simple Medium FunctionDef
- **Type:** cluster
- **Category:** well-documented
- **Occurrences:** 438
- **Confidence:** 35.92%
- **Support:** 22.65%
- **Description:** Pattern with 438 occurrences. Primarily FunctionDef nodes. Average complexity: 1.9, average size: 22.5 lines. Generally well-documented. 

**Examples:**
- `tools/test_cross_repo_pattern_matcher.py:306` - FunctionDef
- `tools/test_api_coordination_hub.py:385` - FunctionDef
- `tools/test_paradigm_translator.py:269` - FunctionDef

### 7. Well-Documented Moderate Large FunctionDef
- **Type:** cluster
- **Category:** well-documented
- **Occurrences:** 110
- **Confidence:** 32.51%
- **Support:** 5.69%
- **Description:** Pattern with 110 occurrences. Primarily FunctionDef nodes. Average complexity: 9.9, average size: 61.0 lines. Generally well-documented. Uses type hints. 

**Examples:**
- `tools/pr-failure-intelligence.py:434` - FunctionDef
- `tools/workflow-orchestrator.py:166` - FunctionDef
- `tools/knowledge_graph_query.py:367` - FunctionDef

### 8. Well-Documented Moderate Large FunctionDef
- **Type:** cluster
- **Category:** well-documented
- **Occurrences:** 111
- **Confidence:** 53.72%
- **Support:** 5.74%
- **Description:** Pattern with 111 occurrences. Primarily FunctionDef nodes. Average complexity: 6.5, average size: 53.9 lines. Generally well-documented. 

**Examples:**
- `tools/dependency-flow-analyzer.py:586` - FunctionDef
- `tools/meta_agent_coordinator.py:697` - FunctionDef
- `tools/cross-repo-pattern-matcher.py:1082` - FunctionDef

### 9. Well-Documented Simple Medium FunctionDef
- **Type:** cluster
- **Category:** well-documented
- **Occurrences:** 280
- **Confidence:** 32.50%
- **Support:** 14.48%
- **Description:** Pattern with 280 occurrences. Primarily FunctionDef nodes. Average complexity: 4.0, average size: 29.8 lines. Generally well-documented. Uses type hints. 

**Examples:**
- `tools/meta_agent_coordinator.py:343` - FunctionDef
- `tools/copilot-usage-tracker.py:344` - FunctionDef
- `tools/validation_utils.py:404` - FunctionDef

### 10. Well-Documented Simple Medium FunctionDef
- **Type:** cluster
- **Category:** well-documented
- **Occurrences:** 129
- **Confidence:** 35.49%
- **Support:** 6.67%
- **Description:** Pattern with 129 occurrences. Primarily FunctionDef nodes. Average complexity: 3.6, average size: 33.1 lines. Generally well-documented. Includes error handling. 

**Examples:**
- `tools/test_archaeology_learner_enhanced.py:245` - FunctionDef
- `tools/test_archaeology_learner_enhanced.py:175` - FunctionDef
- `tools/test_code_smell_fixer.py:443` - FunctionDef

### 11. Anomalous Code Pattern
- **Type:** anomaly
- **Category:** anomaly
- **Occurrences:** 96
- **Confidence:** 80.00%
- **Support:** 4.96%
- **Description:** Code elements that significantly deviate from common patterns

**Examples:**
- `tools/validate-agent-definition.py:37` - ClassDef
- `tools/test_commit_strategy_learner.py:440` - FunctionDef
- `tools/api_coordination_hub.py:449` - FunctionDef

## Key Insights

- **1675** code elements are well-documented
- **96** anomalous code elements detected (potential refactoring candidates)

---
*Report generated by Unsupervised Pattern Learner - @engineer-master*