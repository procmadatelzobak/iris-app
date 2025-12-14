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

# Check for virtual environment
if [ -d "venv" ]; then
    echo "Using virtual environment..."
    PYTHON_CMD="./venv/bin/python"
    PYTEST_CMD="./venv/bin/pytest"
    PLAYWRIGHT_CMD="./venv/bin/playwright"
else
    PYTHON_CMD="python3"
    PYTEST_CMD="pytest"
    PLAYWRIGHT_CMD="playwright"
fi

# Install playwright browsers if needed
$PLAYWRIGHT_CMD install chromium

# Determine mode
if [ "$1" == "--ci" ]; then
    echo "Running in CI mode (headless)..."
    $PYTEST_CMD tests/e2e/test_scenario_a.py -v
else
    echo "Running in headed mode (visible browser)..."
    $PYTEST_CMD tests/e2e/test_scenario_a.py --headed --slowmo 500 -v
fi

echo ""
echo "Test Suite A completed!"
