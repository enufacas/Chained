#!/bin/bash

# Script to organize root directory files
# Created by @organize-guru following clean code principles

set -e

echo "🧹 @organize-guru: Starting root directory cleanup..."

# Move agent-related summaries and reports
echo "📦 Moving agent documentation..."
mv AGENT_ASSIGNMENT_FIX_SUMMARY.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv AGENT_ATTRIBUTION_IMPLEMENTATION_SUMMARY.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv AGENT_DELETION_FIX_DIAGRAM.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv AGENT_DELETION_FIX_SUMMARY.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv AGENT_EVALUATION_COACHING_*.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv AGENT_EVALUATION_DATA_FLOW_ANALYSIS.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv AGENT_EVALUATOR_PIPELINE_IMPLEMENTATION.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv AGENT_EVOLUTION_SUMMARY.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv AGENT_LOCATION_MAPPING.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv AGENT_MISSION_PATTERN_MATCHING_FIX.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv AGENT_NAME_UNIQUENESS_FIX*.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv AGENT_SCORING_ANALYSIS_REPORT.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv AGENT_WORKFLOW_SCENARIO.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv AGENT_WORK_ATTRIBUTION.md docs/implementation-summaries/agents/ 2>/dev/null || true

# Move workflow-related summaries
echo "⚙️  Moving workflow documentation..."
mv ACTIONS_INVESTIGATION_REPORT.md docs/investigations/ 2>/dev/null || true
mv ACTIONS_MIGRATION_EXAMPLE.md docs/implementation-summaries/workflows/ 2>/dev/null || true
mv ACTIONS_RECOMMENDATIONS_SUMMARY.md docs/implementation-summaries/workflows/ 2>/dev/null || true
mv CI_WORKFLOW_VALIDATION_ENHANCEMENT_SUMMARY.md docs/implementation-summaries/workflows/ 2>/dev/null || true
mv WORKFLOW_FIXES_SUMMARY.md docs/implementation-summaries/workflows/ 2>/dev/null || true
mv WORKFLOW_FIX_AGENTOPS_SUMMARY.md docs/implementation-summaries/workflows/ 2>/dev/null || true
mv WORKFLOW_HEALTH_FIX_*.md docs/investigations/ 2>/dev/null || true
mv WORKFLOW_HEALTH_INVESTIGATION_*.md docs/investigations/ 2>/dev/null || true
mv WORKFLOW_OPTIMIZATION.md docs/implementation-summaries/workflows/ 2>/dev/null || true
mv WORKFLOW_SCRIPT_DEPENDENCIES.md docs/implementation-summaries/workflows/ 2>/dev/null || true
mv WORKFLOW_VALIDATION_*.md docs/guides/ 2>/dev/null || true

# Move investigation reports
echo "🔍 Moving investigation reports..."
mv AB_TESTING_BUG_REPORT.md docs/investigations/ 2>/dev/null || true
mv GITHUB_PAGES_HEALTH_INVESTIGATION_*.md docs/investigations/ 2>/dev/null || true
mv INVESTIGATION_*.md docs/investigations/ 2>/dev/null || true
mv LAZY_EVALUATION_ANALYSIS_REPORT.md docs/investigations/ 2>/dev/null || true
mv ROLLOUT_ISSUE_ANALYSIS.md docs/investigations/ 2>/dev/null || true
mv DATA_FLOW_INVESTIGATION_SUMMARY.md docs/investigations/ 2>/dev/null || true

# Move implementation summaries
echo "📝 Moving implementation summaries..."
mv AB_TESTING_IMPLEMENTATION_SUMMARY.md docs/implementation-summaries/features/ 2>/dev/null || true
mv AB_TESTING_SUMMARY.md docs/implementation-summaries/features/ 2>/dev/null || true
mv ARCHAEOLOGY_ENHANCEMENT_IMPLEMENTATION_SUMMARY.md docs/implementation-summaries/features/ 2>/dev/null || true
mv AI_TEST_SUITE_SUMMARY.md docs/implementation-summaries/features/ 2>/dev/null || true
mv CLUSTERING_IMPLEMENTATION_SUMMARY.md docs/implementation-summaries/features/ 2>/dev/null || true
mv CODE_ANALYSIS_FIX_SUMMARY.md docs/implementation-summaries/features/ 2>/dev/null || true
mv COMBINED_LEARNING_IMPLEMENTATION_SUMMARY.md docs/implementation-summaries/features/ 2>/dev/null || true
mv COMBINED_LEARNING_SESSION_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv COMBINED_LEARNING_INFRASTRUCTURE_IMPROVEMENT.md docs/implementation-summaries/infrastructure/ 2>/dev/null || true
mv CONTEXT_AWARE_AGENTS_DESIGN.md docs/architecture/ 2>/dev/null || true
mv CONTEXT_SYSTEM_*.md docs/architecture/ 2>/dev/null || true
mv COORDINATION_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv CREATIVITY_METRICS_IMPLEMENTATION_SUMMARY.md docs/implementation-summaries/features/ 2>/dev/null || true
mv CUSTOM_AGENT_*.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv DEPLOYMENT_SUMMARY.md docs/implementation-summaries/infrastructure/ 2>/dev/null || true
mv DIJKSTRA_FIRST_MISSION_SUMMARY.md docs/implementation-summaries/features/ 2>/dev/null || true
mv ENHANCEMENT_SUMMARY.md docs/implementation-summaries/features/ 2>/dev/null || true
mv FIX_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv HYPOTHESIS_ENGINE_SUMMARY.md docs/implementation-summaries/features/ 2>/dev/null || true
mv IMPLEMENTATION_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv LAZY_EVALUATION_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv MENTOR_SYSTEM_STATUS.md docs/implementation-summaries/features/ 2>/dev/null || true
mv OPTIMIZATION_SUMMARY*.* docs/implementation-summaries/features/ 2>/dev/null || true
mv PAGES_HEALTH_RESOLUTION.md docs/implementation-summaries/infrastructure/ 2>/dev/null || true
mv PIPELINE_*.md docs/implementation-summaries/infrastructure/ 2>/dev/null || true
mv PR_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv PROMPT_GENERATOR_IMPLEMENTATION.md docs/implementation-summaries/features/ 2>/dev/null || true
mv REGISTRY_MERGE_CONFLICT_FIX.md docs/implementation-summaries/infrastructure/ 2>/dev/null || true
mv RENDER_3D_MASTER_CREATION.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv REPETITION_ALERT_RESOLUTION.md docs/implementation-summaries/features/ 2>/dev/null || true
mv SCORING_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv SECURITY_*.md docs/implementation-summaries/infrastructure/ 2>/dev/null || true
mv SEMANTIC_SIMILARITY_IMPLEMENTATION.md docs/implementation-summaries/features/ 2>/dev/null || true
mv SOLUTION_SUMMARY.md docs/implementation-summaries/features/ 2>/dev/null || true
mv SUMMARY-*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv TEMPLATE_ENGINE_IMPLEMENTATION_SUMMARY.md docs/implementation-summaries/features/ 2>/dev/null || true
mv TLDR_LEARNING_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv UNSUPERVISED_LEARNING_COMPLETE.md docs/implementation-summaries/features/ 2>/dev/null || true
mv VISUAL_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv WORLD_MAP_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv WORLD_MODEL_INTEGRATION.md docs/implementation-summaries/features/ 2>/dev/null || true

# Move completion reports
echo "✅ Moving completion reports..."
mv ACCELERATION_COMPLETE.md docs/implementation-summaries/features/ 2>/dev/null || true
mv COACHING_COMPLETE_SUMMARY.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv FOLLOWUP_COMPLETE.md docs/implementation-summaries/features/ 2>/dev/null || true
mv MISSION_COMPLETE*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv MISSION_COMPLETION_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv MISSION_VERIFICATION_COMPLETE.md docs/implementation-summaries/features/ 2>/dev/null || true
mv TASK_COMPLETION_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv AUTONOMOUS_SYSTEM_COMPLETION_REPORT.md docs/implementation-summaries/infrastructure/ 2>/dev/null || true
mv DAILY_REFLECTION_*.md docs/implementation-summaries/features/ 2>/dev/null || true

# Move guides
echo "📚 Moving guides..."
mv AI_AGENT_GUIDE.md docs/guides/ 2>/dev/null || true
mv AI_ORCHESTRATOR_GUIDE.md docs/guides/ 2>/dev/null || true
mv CLOSE_ISSUE_GUIDE.md docs/guides/ 2>/dev/null || true
mv HN_CODE_GENERATOR_GUIDE.md docs/guides/ 2>/dev/null || true
mv KNOWLEDGE_GRAPH_QUICKSTART.md docs/guides/ 2>/dev/null || true
mv LAZY_EVALUATION_QUICKSTART.md docs/guides/ 2>/dev/null || true
mv USAGE_GUIDE.md docs/guides/ 2>/dev/null || true

# Move other documentation
echo "📄 Moving other documentation..."
mv COMPLETION_QUESTIONS.md docs/guides/ 2>/dev/null || true
mv CONTEXT_OPTIONS_ANALYSIS.md docs/architecture/ 2>/dev/null || true
mv DATA_FLOW_ARCHITECTURE_DIAGRAM.md docs/architecture/ 2>/dev/null || true
mv DISTRIBUTED_REGISTRY.md docs/architecture/ 2>/dev/null || true
mv AI_DIVERSITY_SYSTEM_FIX.md docs/architecture/ 2>/dev/null || true
mv EXECUTIVE_SUMMARY*.md docs/implementation-summaries/infrastructure/ 2>/dev/null || true
mv FINAL_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv HANDOVER_TO_CREATE_GURU.md docs/implementation-summaries/features/ 2>/dev/null || true
mv ISSUE_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv LABELS.md docs/guides/ 2>/dev/null || true
mv MISSION_*.md docs/implementation-summaries/features/ 2>/dev/null || true
mv OFFICIAL_DOCS_VERIFICATION.md docs/implementation-summaries/infrastructure/ 2>/dev/null || true
mv PATH_SPECIFIC_CONTEXT_DETAILS.md docs/architecture/ 2>/dev/null || true
mv RECOMMENDATION.md docs/implementation-summaries/features/ 2>/dev/null || true
mv AUTONOMOUS_REFACTORING_AGENT_SUMMARY.md docs/implementation-summaries/agents/ 2>/dev/null || true
mv VERIFICATION_CHECKLIST.md docs/guides/ 2>/dev/null || true
mv analysis-pr-*.md docs/investigations/ 2>/dev/null || true
mv fix-summary.md docs/implementation-summaries/features/ 2>/dev/null || true

# Move Python test files
echo "🧪 Moving test files..."
mv test_*.py tests/ 2>/dev/null || true

# Move utility and migration scripts
echo "🔧 Moving utility scripts..."
mv demonstrate_fix_impact.py scripts/ 2>/dev/null || true
mv migrate_metadata_to_distributed.py scripts/migrations/ 2>/dev/null || true
mv recalculate_all_metrics.py scripts/ 2>/dev/null || true
mv validate_distributed_registry.py scripts/ 2>/dev/null || true
mv verify_agent_sourcing.py scripts/ 2>/dev/null || true
mv run_data_recalculation.sh scripts/ 2>/dev/null || true
mv final_validation.sh scripts/ 2>/dev/null || true
mv test_workflow_optimization.sh tests/ 2>/dev/null || true

# Move JSON files
echo "📊 Moving JSON files..."
mv latest.json docs/data/ 2>/dev/null || true
mv mcp_analysis_results.json analysis/ 2>/dev/null || true

echo "✅ @organize-guru: Root directory cleanup complete!"
echo "📊 Summary:"
echo "  - Markdown files organized by type (implementation, investigation, guides, architecture)"
echo "  - Test files moved to tests/"
echo "  - Scripts organized in scripts/ and scripts/migrations/"
echo "  - Core documentation remains in root"
