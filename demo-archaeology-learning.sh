#!/bin/bash
# Demonstration script for Enhanced Code Archaeology with Active Learning

set -e

echo "=========================================="
echo "Enhanced Code Archaeology - Demo"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Testing Archaeology Learner...${NC}"
echo ""
python3 tools/test_archaeology_learner.py
echo ""

echo -e "${GREEN}✅ All archaeology learner tests passed!${NC}"
echo ""

echo -e "${BLUE}2. Testing Original Archaeology Tool...${NC}"
echo ""
python3 tools/test_code_archaeologist.py
echo ""

echo -e "${GREEN}✅ All original archaeology tests passed!${NC}"
echo ""

echo -e "${BLUE}3. Running Integration Test...${NC}"
echo ""
echo "Running archaeology with learning enabled..."
python3 tools/code-archaeologist.py --learn -n 50 -o /tmp/demo_report.md 2>&1 | tail -20
echo ""

echo -e "${GREEN}✅ Integration test completed!${NC}"
echo ""

echo -e "${BLUE}4. Checking Generated Files...${NC}"
echo ""

if [ -f "analysis/archaeology.json" ]; then
    echo -e "${GREEN}✓${NC} archaeology.json exists"
else
    echo -e "${YELLOW}⚠${NC} archaeology.json not found"
fi

if [ -f "analysis/archaeology-patterns.json" ]; then
    echo -e "${GREEN}✓${NC} archaeology-patterns.json exists"
    echo ""
    echo "Pattern database contents:"
    cat analysis/archaeology-patterns.json | jq '{version, last_updated, patterns: (.patterns | {success: (.success | length), failure: (.failure | length), evolution: (.evolution | length)}), insights: (.insights | length), recommendations: (.recommendations | length), statistics}' 2>/dev/null || cat analysis/archaeology-patterns.json | head -30
else
    echo -e "${YELLOW}⚠${NC} archaeology-patterns.json not found"
fi

echo ""
echo -e "${BLUE}5. Documentation Check...${NC}"
echo ""

if [ -f "docs/archaeology-learner.md" ]; then
    lines=$(wc -l < docs/archaeology-learner.md)
    echo -e "${GREEN}✓${NC} docs/archaeology-learner.md exists ($lines lines)"
else
    echo -e "${YELLOW}⚠${NC} docs/archaeology-learner.md not found"
fi

if [ -f "ARCHAEOLOGY_LEARNING_IMPLEMENTATION.md" ]; then
    lines=$(wc -l < ARCHAEOLOGY_LEARNING_IMPLEMENTATION.md)
    echo -e "${GREEN}✓${NC} ARCHAEOLOGY_LEARNING_IMPLEMENTATION.md exists ($lines lines)"
else
    echo -e "${YELLOW}⚠${NC} ARCHAEOLOGY_LEARNING_IMPLEMENTATION.md not found"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Demo Complete!${NC}"
echo "=========================================="
echo ""
echo "Key Features Demonstrated:"
echo "  ✓ Pattern learning from git history"
echo "  ✓ Success/failure pattern identification"
echo "  ✓ Evolution pattern tracking"
echo "  ✓ Predictive insights generation"
echo "  ✓ Proactive recommendations"
echo "  ✓ Integration with existing tools"
echo "  ✓ Comprehensive test coverage"
echo ""
echo "Next Steps:"
echo "  1. Review the pattern database: analysis/archaeology-patterns.json"
echo "  2. Read the documentation: docs/archaeology-learner.md"
echo "  3. Check the implementation summary: ARCHAEOLOGY_LEARNING_IMPLEMENTATION.md"
echo "  4. Run with more commits: python3 tools/archaeology-learner.py -n 500"
echo ""
