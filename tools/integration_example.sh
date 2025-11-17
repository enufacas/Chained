#!/bin/bash
# Integration Example: Adding A/B Testing to an Existing Workflow
# 
# This script demonstrates how to integrate autonomous A/B testing
# into an existing GitHub Actions workflow.
#
# Author: @accelerate-specialist

set -e

WORKFLOW_NAME="example-workflow"

echo "🔬 A/B Testing Integration Example"
echo "======================================"
echo ""
echo "This demonstrates integrating A/B testing into: ${WORKFLOW_NAME}"
echo ""

# Step 1: Check if there's an active experiment
echo "📋 Step 1: Check for Active Experiment"
echo "----------------------------------------"

cat << 'EOF'
- name: Check for A/B Test
  id: ab_test
  run: |
    # Get variant for this workflow
    result=$(python3 tools/ab_testing_helper.py get-variant "${WORKFLOW_NAME}" || echo '{"has_experiment": false}')
    
    has_experiment=$(echo "$result" | jq -r '.has_experiment')
    variant=$(echo "$result" | jq -r '.variant // "control"')
    
    echo "has_experiment=${has_experiment}" >> $GITHUB_OUTPUT
    echo "variant=${variant}" >> $GITHUB_OUTPUT
    
    if [ "$has_experiment" == "true" ]; then
      experiment_id=$(echo "$result" | jq -r '.experiment_id')
      config=$(echo "$result" | jq -c '.variant_config')
      echo "experiment_id=${experiment_id}" >> $GITHUB_OUTPUT
      echo "config=${config}" >> $GITHUB_OUTPUT
      
      echo "🔬 Using variant: ${variant}"
      echo "📝 Config: ${config}"
    else
      echo "ℹ️  No active experiment, using default configuration"
    fi
EOF

echo ""
echo "✅ This step checks for an active experiment and retrieves the variant"
echo ""

# Step 2: Apply the configuration
echo "📋 Step 2: Apply Variant Configuration"
echo "----------------------------------------"

cat << 'EOF'
- name: Apply Configuration
  id: config
  env:
    HAS_EXPERIMENT: ${{ steps.ab_test.outputs.has_experiment }}
    CONFIG: ${{ steps.ab_test.outputs.config }}
  run: |
    if [ "$HAS_EXPERIMENT" == "true" ]; then
      # Extract configuration values
      timeout=$(echo "${CONFIG}" | jq -r '.timeout // 300')
      max_retries=$(echo "${CONFIG}" | jq -r '.max_retries // 3')
      batch_size=$(echo "${CONFIG}" | jq -r '.batch_size // 10')
      
      echo "⚙️  Applying variant configuration:"
      echo "   Timeout: ${timeout}s"
      echo "   Max Retries: ${max_retries}"
      echo "   Batch Size: ${batch_size}"
      
      # Export for use in subsequent steps
      echo "timeout=${timeout}" >> $GITHUB_OUTPUT
      echo "max_retries=${max_retries}" >> $GITHUB_OUTPUT
      echo "batch_size=${batch_size}" >> $GITHUB_OUTPUT
    else
      # Use defaults
      echo "timeout=300" >> $GITHUB_OUTPUT
      echo "max_retries=3" >> $GITHUB_OUTPUT
      echo "batch_size=10" >> $GITHUB_OUTPUT
    fi
EOF

echo ""
echo "✅ This step extracts and applies the configuration from the variant"
echo ""

# Step 3: Run your workflow with the configuration
echo "📋 Step 3: Execute with Variant Configuration"
echo "-----------------------------------------------"

cat << 'EOF'
- name: Run Workflow Task
  id: task
  timeout-minutes: ${{ fromJSON(steps.config.outputs.timeout) / 60 }}
  env:
    MAX_RETRIES: ${{ steps.config.outputs.max_retries }}
    BATCH_SIZE: ${{ steps.config.outputs.batch_size }}
  run: |
    start_time=$(date +%s)
    
    # Your actual workflow logic here
    # Use the configuration variables
    echo "🚀 Running with configuration:"
    echo "   MAX_RETRIES: ${MAX_RETRIES}"
    echo "   BATCH_SIZE: ${BATCH_SIZE}"
    
    # Simulate work
    python3 << 'PYTHON_SCRIPT'
    import os
    import time
    import random
    
    max_retries = int(os.environ.get('MAX_RETRIES', 3))
    batch_size = int(os.environ.get('BATCH_SIZE', 10))
    
    print(f"Processing with batch_size={batch_size}, max_retries={max_retries}")
    
    # Simulate processing
    success = random.random() > 0.1  # 90% success rate
    time.sleep(1)  # Simulate work
    
    if success:
        print("✅ Task completed successfully")
        exit(0)
    else:
        print("❌ Task failed")
        exit(1)
    PYTHON_SCRIPT
    
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo "duration=${duration}" >> $GITHUB_OUTPUT
    echo "success=true" >> $GITHUB_OUTPUT
EOF

echo ""
echo "✅ This step runs your actual workflow logic with the variant config"
echo ""

# Step 4: Record metrics
echo "📋 Step 4: Record Performance Metrics"
echo "---------------------------------------"

cat << 'EOF'
- name: Record A/B Test Metrics
  if: always() && steps.ab_test.outputs.has_experiment == 'true'
  env:
    EXPERIMENT_ID: ${{ steps.ab_test.outputs.experiment_id }}
    VARIANT: ${{ steps.ab_test.outputs.variant }}
  run: |
    # Calculate metrics
    duration=${{ steps.task.outputs.duration }}
    success_rate=${{ steps.task.outputs.success == 'true' && '1.0' || '0.0' }}
    
    # Record the sample
    python3 tools/ab_testing_helper.py record \
      "${EXPERIMENT_ID}" \
      "${VARIANT}" \
      --metric execution_time="${duration}" \
      --metric success_rate="${success_rate}" \
      --metadata run_id="${{ github.run_id }}" \
      --metadata run_attempt="${{ github.run_attempt }}"
    
    echo "📊 Recorded metrics:"
    echo "   Execution time: ${duration}s"
    echo "   Success rate: ${success_rate}"
EOF

echo ""
echo "✅ This step records metrics back to the A/B testing system"
echo ""

# Complete example
echo "📋 Complete Workflow Example"
echo "=============================="
echo ""
echo "Here's a complete minimal workflow with A/B testing:"
echo ""

cat << 'EOF' > /tmp/example-ab-testing-workflow.yml
name: Example Workflow with A/B Testing

on:
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:

jobs:
  run-with-ab-testing:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Check for A/B Test
        id: ab_test
        run: |
          result=$(python3 tools/ab_testing_helper.py get-variant "example-workflow" || echo '{"has_experiment": false}')
          has_experiment=$(echo "$result" | jq -r '.has_experiment')
          variant=$(echo "$result" | jq -r '.variant // "control"')
          echo "has_experiment=${has_experiment}" >> $GITHUB_OUTPUT
          echo "variant=${variant}" >> $GITHUB_OUTPUT
          if [ "$has_experiment" == "true" ]; then
            echo "experiment_id=$(echo "$result" | jq -r '.experiment_id')" >> $GITHUB_OUTPUT
            echo "config=$(echo "$result" | jq -c '.variant_config')" >> $GITHUB_OUTPUT
          fi
      
      - name: Apply Configuration
        id: config
        if: steps.ab_test.outputs.has_experiment == 'true'
        env:
          CONFIG: ${{ steps.ab_test.outputs.config }}
        run: |
          timeout=$(echo "${CONFIG}" | jq -r '.timeout // 300')
          echo "timeout=${timeout}" >> $GITHUB_OUTPUT
      
      - name: Run Task
        id: task
        run: |
          start_time=$(date +%s)
          
          # Your workflow logic here
          echo "Running task..."
          sleep 2
          
          end_time=$(date +%s)
          duration=$((end_time - start_time))
          echo "duration=${duration}" >> $GITHUB_OUTPUT
          echo "success=true" >> $GITHUB_OUTPUT
      
      - name: Record Metrics
        if: always() && steps.ab_test.outputs.has_experiment == 'true'
        env:
          EXPERIMENT_ID: ${{ steps.ab_test.outputs.experiment_id }}
          VARIANT: ${{ steps.ab_test.outputs.variant }}
        run: |
          python3 tools/ab_testing_helper.py record \
            "${EXPERIMENT_ID}" \
            "${VARIANT}" \
            --metric execution_time="${{ steps.task.outputs.duration }}" \
            --metric success_rate="${{ steps.task.outputs.success == 'true' && '1.0' || '0.0' }}"
EOF

cat /tmp/example-ab-testing-workflow.yml

echo ""
echo "✅ Saved to: /tmp/example-ab-testing-workflow.yml"
echo ""

# Summary
echo "📚 Integration Summary"
echo "======================"
echo ""
echo "To integrate A/B testing into your workflow:"
echo ""
echo "1. Add the 'Check for A/B Test' step at the beginning"
echo "2. Apply configuration from the variant"
echo "3. Run your workflow logic using the configuration"
echo "4. Record performance metrics at the end"
echo ""
echo "The autonomous system will:"
echo "- Create experiments automatically"
echo "- Analyze results using Bayesian statistics"
echo "- Determine winners with high confidence"
echo "- Create rollout issues for deployment"
echo ""
echo "✨ That's it! Your workflow now participates in autonomous optimization."
echo ""
echo "For more information:"
echo "  📖 docs/AUTONOMOUS_AB_TESTING.md"
echo "  🔬 tools/demo_autonomous_ab_testing.py"
echo "  🧪 tests/test_autonomous_ab_testing.py"
echo ""
