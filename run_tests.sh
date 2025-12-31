#!/bin/bash
# Test runner for enhanced remove-source features

set -e  # Exit on error

echo "====================================="
echo "  Remove-Source Test Suite"
echo "====================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Activate virtual environment
if [ -d "venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${RED}Error: venv not found. Run: python3 -m venv venv${NC}"
    exit 1
fi

# Install test dependencies
echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install -q pytest pytest-cov

echo ""
echo "====================================="
echo "  Unit Tests"
echo "====================================="

# Run backup manager tests
echo -e "${YELLOW}Testing: Backup Manager${NC}"
pytest tests/test_source_backup_manager.py -v

# Run analytics tests
echo -e "${YELLOW}Testing: Analytics System${NC}"
pytest tests/test_source_analytics.py -v

# Run remove command tests
echo -e "${YELLOW}Testing: Remove Command${NC}"
pytest tests/test_remove_source_command.py -v

# Run bundle manager tests
echo -e "${YELLOW}Testing: Bundle Manager${NC}"
pytest tests/test_bundle_manager_remove.py -v

echo ""
echo "====================================="
echo "  Coverage Report"
echo "====================================="

pytest tests/ -v \
    --cov=core.source_system.source_backup_manager \
    --cov=core.source_system.source_analytics \
    --cov=core.source_system.remove_source_command \
    --cov=core.source_system.enhanced_remove_command \
    --cov=core.source_system.bundle_manager \
    --cov-report=term-missing \
    --cov-report=html

echo ""
echo -e "${GREEN}All tests passed!${NC}"
echo ""
echo "Coverage report: htmlcov/index.html"
echo ""
echo "====================================="
echo "  Quick Manual Test"
echo "====================================="
echo ""
echo "Run these commands to test manually:"
echo ""
echo "  1. List sources:"
echo "     ./capcat list sources"
echo ""
echo "  2. Dry-run removal:"
echo "     ./capcat remove-source --dry-run"
echo ""
echo "  3. Remove with backup:"
echo "     ./capcat remove-source"
echo ""
echo "  4. Undo removal:"
echo "     ./capcat remove-source --undo"
echo ""
echo "  5. Check backups:"
echo "     ls -la ../.capcat_backups/"
echo ""
echo "====================================="