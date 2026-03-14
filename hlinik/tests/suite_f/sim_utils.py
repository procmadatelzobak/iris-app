"""
Suite F: Simulation Utilities
=============================
Shared constants and error handling helpers.
"""

import time
from pathlib import Path

# Constants
TEST_PORT = 8003
BASE_URL = f"http://localhost:{TEST_PORT}"
SCREENSHOT_DIR = Path("docs/suite_f_screenshots")


def generate_bug_report(step_name: str, error: str, context: str = ""):
    """Generate a Markdown bug report for a failed step."""
    report_path = Path("docs/BUG_REPORT_SUITE_F.md")
    
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    
    content = f"""# BUG REPORT: Suite F Failure

**Generated:** {timestamp}
**Failed Step:** {step_name}

## Error Details
```
{error}
```

## Context
{context}

## Artifacts
- Screenshot: `docs/suite_f_screenshots/FAILURE_{step_name}.png`
- DOM Dump: `docs/suite_f_screenshots/FAILURE_{step_name}.html`

## Expected Behavior
The step should have completed without error as part of The Grand Simulation.

## Actual Behavior
The test failed at step `{step_name}` with the error shown above.
"""
    
    report_path.write_text(content)
    print(f"\n⚠️  Bug Report Generated: {report_path}")


def capture_failure(step_name: str, page, error: str, context: str = ""):
    """
    Capture failure artifacts when a step fails:
    1. Screenshot
    2. DOM HTML dump
    3. Bug Report markdown
    """
    from pathlib import Path
    
    screenshot_path = Path(f"docs/suite_f_screenshots/FAILURE_{step_name}.png")
    html_path = Path(f"docs/suite_f_screenshots/FAILURE_{step_name}.html")
    
    try:
        page.screenshot(path=str(screenshot_path))
        print(f"📸 Failure screenshot: {screenshot_path}")
    except Exception as e:
        print(f"⚠️  Could not capture screenshot: {e}")
    
    try:
        html_path.write_text(page.content())
        print(f"📄 DOM dump: {html_path}")
    except Exception as e:
        print(f"⚠️  Could not dump DOM: {e}")
    
    generate_bug_report(step_name, str(error), context)
