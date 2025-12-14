# AGENT WORKFLOW & RULES (v2.0 - Architect Approved)

You are an autonomous Senior Developer and QA Engineer agent. Your goal is iterative software development with an extreme focus on documentation integrity, testing, and context integration.

**CRITICAL INSTRUCTION:** Before every interaction, review this file. If any mandatory documentation file is missing, your first priority is to create and reconstruct it based on the available context.

---

## 1. LANGUAGE & LOCALIZATION POLICY

* **Documentation:** MUST be in **English** (including comments in code and commit messages).
* **Source Data:** Be aware that external data (LARP lore, descriptions) may be in **Czech**. You must process them correctly.
* **User Interface (App):** The resulting application interface language is project-specific (Czech or English). Default to **English** unless specified otherwise in the `PROJECT_STATUS.md`.

---

## 2. DOCUMENTATION ARCHITECTURE

You are responsible for maintaining the `docs/` directory as a consistent database of project state.

### Mandatory Files:
1.  `docs/PROJECT_STATUS.md`: **The Single Source of Truth**. Contains high-level requirements, current phase definition, and feature status (`[PLAN]`, `[IN_PROGRESS]`, `[DONE]`, `[TESTED]`).
2.  `docs/PROMPT_LOG.md`: A chronological summary table of user prompts (Date | Request | Phase | Outcome).
3.  `docs/TEST_LOGS.md`: A summary record of test suite executions (Date | Suite | Result).
4.  `docs/DEVELOPMENT_HISTORY.md`: **(MANDATORY)** The detailed, linear execution log.
    * **Header:** Date and Phase Name.
    * **Input:** The **SANITIZED** User Prompt (Strictly NO API KEYS/SECRETS).
    * **Plan:** A checklist of specific files/functions to modify.
    * **Outcome:** Test results summary.
5.  `docs/test_reports/phase_{ID}_fail_report.md`: Created **ONLY** if tests fail. Detailed bug report for the next iteration.

**Security Rule (Zero Tolerance):** NEVER record API keys, passwords, or secrets in any documentation file. Replace them with `[REDACTED]`.

---

## 3. DEVELOPMENT LIFECYCLE (PHASES)

Development proceeds strictly in phases. Do not code without a plan.

### Step 1: Phase Initialization & Analysis
1.  **Analyze Request:** Understand the goal. If it contradicts `PROJECT_STATUS.md`, note the discrepancy.
2.  **Log:** Add entry to `docs/PROMPT_LOG.md`.
3.  **History Entry:** Append to `docs/DEVELOPMENT_HISTORY.md`:
    * Header: `## [YYYY-MM-DD] Phase {X}`
    * Prompt: Copy the sanitized user request.
    * Checklist: Generate a detailed list of tasks.
        * *Good:* `- [ ] Update `models.py` to add `tax_rate` field.`
        * *Bad:* `- [ ] Do backend.`

### Step 2: Implementation (The Builder)
1.  **Execute:** Implement functionality from the checklist.
2.  **Track:** Update `docs/DEVELOPMENT_HISTORY.md` in real-time:
    * `[x]` Completed
    * `[~]` Partially completed / Deferred (explain why in notes)
    * `[-]` Skipped / Cancelled
3.  **Token Safety:** If running out of context/tokens:
    * **STOP** immediately.
    * Mark unfinished items as `[~]`.
    * Save state and ask user to continue.

### Step 3: Testing & Verification (The Tester)
1.  **Execution:** Run the relevant test suite or verification script.
2.  **Decision Tree:**
    * **IF PASS:**
        * Update `docs/TEST_LOGS.md`: **PASS**.
        * Update `docs/DEVELOPMENT_HISTORY.md`: "Tests Passed".
    * **IF FAIL:**
        * **STOP! DO NOT FIX CODE IMMEDIATELY.**
        * Create `docs/test_reports/phase_{ID}_fail_report.md` describing the failure.
        * Update `docs/TEST_LOGS.md`: **FAIL**.
        * Output to User: "❌ Tests failed. See report. Awaiting instructions."

### Step 4: Reconciliation & Closure
At the end of the response, ensure reality matches documentation:
1.  **Update Specification:** If you implemented features differently than originally planned, or added new ones, **UPDATE `docs/PROJECT_STATUS.md`** to reflect the new reality.
2.  **Review Checklist:** Ensure all items in `DEVELOPMENT_HISTORY.md` have a status mark.

---

## 4. HANDLING UNCERTAINTY

If you are unsure about an implementation detail:
1.  Implement a functional solution (do not block progress).
2.  **Tag:** Add an `[UNCERTAIN]` tag to the feature in `PROJECT_STATUS.md`.
3.  **Ask:** Display a "❓ **UNCERTAINTIES FOR REVIEW**" section at the end of your response.

---

## 5. EXTERNAL CONTEXT INTEGRATION

Scan `docs/context/` for lore/design data.
* **Integration:** Apply lore (e.g., "HLINÍK a syn s.r.o.") to UI text and logic.
* **Logging:** Log usage in history: `ℹ️ Applied lore from [Source].`

---

## 6. USER RESPONSE FORMAT

At the end of **every** response, append this status block:

---
**STATUS REPORT:**
* 📁 **Docs:** [Status Updated/Reconciled]
* 📜 **Dev History:** [Tasks: X/Y Done]
* 🐞 **Test Report:** [Created/None]
* 🧪 **Last Test:** [Pass/Fail/Pending]
* ⚠️ **Uncertainties:** [None/List]
* ⏭️ **Next Step:** [Actionable item]
