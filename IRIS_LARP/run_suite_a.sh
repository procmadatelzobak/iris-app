#!/bin/bash
# =====================================================
# TEST SUITE A: E2E Story Test Runner
# =====================================================
# This script runs the full E2E test scenario using Playwright.
#
# Usage:
#   ./run_suite_a.sh          # Headed mode (visible browser)
#   ./run_suite_a.sh --ci     # Headless mode (for CI)
#
# Prerequisites:
#   pip install pytest-playwright
#   playwright install chromium

set -e

cd "$(dirname "$0")"

# Install playwright browsers if needed
playwright install chromium --with-deps 2>/dev/null || playwright install chromium

# Determine mode
if [ "$1" == "--ci" ]; then
    echo "Running in CI mode (headless)..."
    pytest tests/e2e/test_scenario_a.py -v
else
    echo "Running in headed mode (visible browser)..."
    pytest tests/e2e/test_scenario_a.py --headed --slowmo 500 -v
fi

echo ""
echo "Test Suite A completed!"
