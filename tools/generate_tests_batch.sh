#!/bin/bash
# 
# Batch Test Generation Script
# 
# Usage: ./generate_tests_batch.sh [directory]
# 
# Generates AI-powered tests for all Python files in the specified directory.
# If no directory is specified, uses 'tools/' as default.
#
# Created by @investigate-champion

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get directory from argument or use default
TARGET_DIR="${1:-tools}"

echo "======================================================================"
echo "🤖 Batch AI Test Generation"
echo "   by @investigate-champion"
echo "======================================================================"
echo ""
echo "Target directory: $TARGET_DIR"
echo ""

# Counter variables
total_files=0
generated_tests=0
failed_files=0
total_test_cases=0

# Find all Python files (excluding test files and __init__.py)
for file in "$TARGET_DIR"/*.py; do
    # Skip if no files found
    [ -e "$file" ] || continue
    
    # Get filename
    filename=$(basename "$file")
    
    # Skip test files and __init__.py
    if [[ "$filename" == test_* ]] || [[ "$filename" == "__init__.py" ]]; then
        echo -e "${YELLOW}⏭️  Skipping: $filename${NC}"
        continue
    fi
    
    total_files=$((total_files + 1))
    
    echo -e "${GREEN}🔍 Processing: $filename${NC}"
    
    # Generate tests
    if python3 tools/ai_test_generator.py "$file" 2>&1 | tee /tmp/test_gen_output.txt; then
        # Extract number of test cases generated from output
        test_count=$(grep -oP 'Generated \K\d+' /tmp/test_gen_output.txt | head -1)
        
        if [ -n "$test_count" ]; then
            generated_tests=$((generated_tests + 1))
            total_test_cases=$((total_test_cases + test_count))
            echo -e "   ${GREEN}✅ Generated $test_count test cases${NC}"
        else
            echo -e "   ${YELLOW}⚠️  No tests generated${NC}"
        fi
    else
        failed_files=$((failed_files + 1))
        echo -e "   ${RED}❌ Failed to generate tests${NC}"
    fi
    
    echo ""
done

# Print summary
echo "======================================================================"
echo "📊 Generation Summary"
echo "======================================================================"
echo "Files processed: $total_files"
echo -e "Tests generated: ${GREEN}$generated_tests${NC}"
echo -e "Failed: ${RED}$failed_files${NC}"
echo "Total test cases: $total_test_cases"
echo ""

if [ $generated_tests -gt 0 ]; then
    echo "To run all generated tests:"
    echo "  for f in tests/test_ai_gen_*.py; do python3 \$f; done"
    echo ""
fi

# Exit with error if any files failed
if [ $failed_files -gt 0 ]; then
    exit 1
fi

exit 0
