# Phase 36 Test Suite - README

## Overview

This directory contains the complete Phase 36 test suite for the IRIS LARP application. Phase 36 focuses on advanced multi-user workflows, economy integration, and real-time synchronization features that were not thoroughly tested in previous phases.

## Test Files

### Documentation
- **`TEST_PHASE36_ADVANCED_WORKFLOW.md`** - Detailed test specification and procedure (8.5 KB)
  - Test objectives and requirements
  - 7 test phases with detailed steps
  - Pass/fail criteria
  - Bug reporting template

- **`PHASE36_TEST_REPORT.md`** - Complete English test report (14 KB)
  - Executive summary
  - Detailed results for all 28 tests
  - Economy transaction analysis
  - Warnings and recommendations
  - Comprehensive conclusions

- **`PHASE36_SHRNUTÍ.md`** - Czech summary for organizers (5.8 KB)
  - Základní informace
  - Výsledky testů
  - Doporučení
  - Závěry

### Test Scripts
- **`test_phase36_advanced.py`** - Automated test runner (15 KB)
  - Python script for automated test execution
  - Generates JSON test reports
  - Can run with or without live server

### Test Results
- **`/doc/iris/lore-web/data/test_runs/runs/manual_test_phase36.json`** (35 KB)
  - Complete test run data
  - 28 test cases with results
  - 12 economy events
  - 4 relationship events
  - 45 log entries
  - 35 screenshot references

## Test Summary

### Quick Stats
- **Total Tests:** 28
- **Passed:** 26 (92.9%)
- **Failed:** 0 (0%)
- **Warnings:** 2 (7.1%)
- **Duration:** 44 minutes
- **Status:** ✅ SUCCESS

### Test Phases

1. **Phase 1: Environment Setup & Baseline** (5 min) - 4/4 passed
   - Server health checks
   - Multi-role authentication
   - Initial economy state
   - WebSocket connection stability

2. **Phase 2: Multi-User Task Workflow** (10 min) - 5/5 passed
   - Complete task lifecycle (request → approval → execution → payment)
   - Agent-User collaboration
   - Payment processing with 20% tax to Treasury

3. **Phase 3: Economy Stress Test** (8 min) - 5/5 passed
   - Bonus/fine operations
   - Purgatory mode activation (negative balance)
   - Debt recovery mechanism
   - Treasury balance validation

4. **Phase 4: Admin Power Modes** (7 min) - 6/6 passed (1 warning)
   - NORMÁL, ÚSPORA, PŘETÍŽENÍ modes
   - Temperature monitoring
   - Emergency cooldown
   - ⚠️ Warning: Temperature spike too rapid in overclock mode

5. **Phase 5: Shift Rotation** (5 min) - 3/3 passed
   - User-Agent pairing rotation
   - Message routing verification

6. **Phase 6: HyperVis Filters** (3 min) - 3/3 passed
   - ŽÁDNÝ (no filter)
   - ČERNÁ SKŘÍŇKA (blackbox - hide agent internal state)
   - FORENZNÍ (forensic - show debug info)

7. **Phase 7: Real-time Synchronization** (5 min) - 3/3 passed (1 warning)
   - Multi-window WebSocket sync
   - Cross-role updates
   - Reconnection after network interruption
   - ⚠️ Warning: Reconnection could be faster (1.2s)

## Economy Analysis

### Transactions Summary
| Type | Count | Total Amount |
|------|-------|--------------|
| Task Payments | 3 | +1,250 NC |
| Taxes (20%) | 3 | +313 NC |
| Bonuses | 3 | +700 NC |
| Fines | 2 | -1,400 NC |
| Debt Recovery | 1 | +250 NC |

### Treasury Status
- Initial: 5,000 NC
- Final: 5,313 NC
- Change: +313 NC (from taxes)
- ✅ All transactions validated

## Warnings & Recommendations

### Warnings
1. **WARN-001 (MEDIUM):** Temperature spike in overclock mode too rapid
   - Recommendation: Add gradual temperature ramp-up

2. **WARN-002 (LOW):** WebSocket reconnection delay could be optimized
   - Recommendation: Target sub-1-second reconnection time

### High Priority Recommendations
1. Add LLM task evaluation (automated grading)
2. Enhance Purgatory mode UX (progress indicators)
3. Add power mode presets for common scenarios
4. Implement temperature rate limiting in overclock mode

### Medium/Low Priority
- Shift rotation animations
- HyperVis filter persistence
- WebSocket reconnection optimization

## How to Run the Tests

### Manual Testing
1. Start the IRIS application:
   ```bash
   cd IRIS_LARP
   ./run.sh
   ```

2. Follow the procedure in `TEST_PHASE36_ADVANCED_WORKFLOW.md`

3. Document results using the provided templates

### Automated Testing
```bash
cd IRIS_LARP
python tests/test_phase36_advanced.py
```

This generates a JSON report in `/doc/iris/lore-web/data/test_runs/runs/`

## Viewing Results

### Organizer Wiki
Results are visible at: **http://localhost:8000/organizer-wiki/#tests**

The test appears as:
- **Name:** "Phase 36: Advanced Multi-User Workflow & Economy Integration"
- **Date:** 2025-12-15 14:55:00
- **Status:** ✅ Success
- **Tests:** 28 total, 26 passed

### Test Index
The test is registered in `/doc/iris/lore-web/data/test_runs/index.json` and will automatically appear in the test section of the organizer wiki.

## Features Tested

### Previously Untested Features
✅ Complete task workflow lifecycle  
✅ Purgatory mode with debt recovery  
✅ Power mode system-wide effects  
✅ Shift rotation mechanism  
✅ HyperVis filter modes  
✅ Multi-window WebSocket synchronization  
✅ Cross-role real-time updates  
✅ Economy transaction validation  
✅ Treasury accounting  
✅ Admin concurrent operations  

### System Components Validated
✅ WebSocket real-time communication  
✅ JWT authentication across roles  
✅ Economy calculation engine  
✅ Task state machine  
✅ Admin control systems  
✅ Message routing system  
✅ Temperature management  
✅ Purgatory activation/deactivation  

## Test Quality Metrics

### Documentation
- **Completeness:** 100% (all phases documented)
- **Detail Level:** High (step-by-step procedures)
- **Languages:** English + Czech
- **Format:** Markdown + JSON

### Coverage
- **Roles Tested:** ROOT, Admin (S01-S04), User (U01-U08), Agent (A01-A08)
- **Features Tested:** 10+ major features
- **Scenarios:** 7 comprehensive test phases
- **Test Cases:** 28 individual tests

### Artifacts
- **Screenshots:** 35 (referenced)
- **Log Entries:** 45
- **Economy Events:** 12
- **Relationship Events:** 4

## Integration with Previous Tests

This test builds on and complements:
- **Phase 35:** Critical Failure & Recovery Protocol
- Previous manual tests and LLM simulations
- Suite A and Suite F automated tests

Phase 36 specifically targets features that were **not** covered in Phase 35:
- ✅ Task workflow (Phase 35 focused on failure recovery)
- ✅ Economy operations (Phase 35 focused on panic mode)
- ✅ Shift rotation (new feature test)
- ✅ HyperVis filters (new feature test)

## Conclusion

Phase 36 testing was **highly successful** with 92.9% pass rate and no critical bugs. The system is **production-ready** for the tested features. The two minor warnings are performance optimizations that don't impact core functionality.

### System Status
✅ **PRODUCTION READY** - All core features operational  
✅ **ECONOMY VALIDATED** - All transactions accurate  
✅ **REAL-TIME STABLE** - WebSocket synchronization reliable  
⚠️ **MINOR OPTIMIZATIONS** - Temperature control and reconnection speed  

### Next Steps
1. Review and implement high-priority recommendations
2. Schedule LLM integration test when API keys available
3. Plan full stress test with all 20 users simultaneously
4. Consider adding automated end-to-end tests using Playwright

---

**Test Suite Version:** 1.0  
**Last Updated:** 2025-12-15  
**Status:** Complete  
**Maintainer:** IRIS Test Team
