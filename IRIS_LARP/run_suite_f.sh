#!/bin/bash
# Suite F: The Grand Simulation
# Entry point for the massive E2E incident simulation

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       SUITE F: THE GRAND SIMULATION                          ║"
echo "║       Phase 34 - Incident Lifecycle E2E Test                 ║"
echo "╚══════════════════════════════════════════════════════════════╝"

# Detect venv
if [ -d "venv" ]; then
    echo "Using virtual environment..."
    PYTHON_CMD="./venv/bin/python"
    PYTEST_CMD="./venv/bin/pytest"
    PLAYWRIGHT_CMD="./venv/bin/playwright"
else
    echo "Using global Python..."
    PYTHON_CMD="python3"
    PYTEST_CMD="pytest"
    PLAYWRIGHT_CMD="playwright"
fi

# Ensure Playwright is installed
$PLAYWRIGHT_CMD install chromium 2>/dev/null || true

# Ensure screenshots directory exists
mkdir -p docs/suite_f_screenshots

# Parse arguments
HEADED=""
if [ "$1" == "--ci" ]; then
    echo "Running in CI mode (headless)..."
    # Default is headless, so we don't need a flag
else
    echo "Running in headed mode (visible browsers)..."
    HEADED="--headed"
fi

# Run the test
$PYTEST_CMD tests/suite_f/test_grand_simulation.py \
    -v \
    --browser chromium \
    $HEADED \
    -s

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║       SIMULATION COMPLETE                                     ║"
echo "║       Screenshots: docs/suite_f_screenshots/                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
