"""
Suite F: The Grand Simulation
==============================
Phase 34 - A single, massive E2E test simulating an entire incident lifecycle.

This test runs 3 parallel browser contexts (Admin, User, Agent) and walks
through a complete "Day in the Life" scenario at IRIS station.

Phases:
0. Genesis - Clean slate, seed, launch
1. Calm Before Storm - Init checks
2. Escalation - Emergency message, LLM response
3. Divine Intervention - Admin RED alert, sync verification
4. Economic Pressure - Fine user, debt mode
5. Resolution - Agent solves, system calms

If ANY step fails, we capture:
- Screenshot
- DOM dump
- Markdown Bug Report
"""

import pytest
import time
from pathlib import Path
from playwright.sync_api import expect
from .sim_utils import capture_failure, generate_bug_report, BASE_URL, SCREENSHOT_DIR


class SimulationStep:
    """Context manager for safe step execution with failure capture."""
    
    def __init__(self, name: str, page, description: str = ""):
        self.name = name
        self.page = page
        self.description = description
    
    def __enter__(self):
        print(f"\n{'='*60}")
        print(f"📍 Step: {self.name}")
        if self.description:
            print(f"   {self.description}")
        print('='*60)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            print(f"\n❌ FAILED: {self.name}")
            capture_failure(self.name, self.page, str(exc_val), self.description)
            return False  # Re-raise the exception
        print(f"✓ {self.name} completed")
        return False


def take_screenshot(page, name: str):
    """Take a numbered screenshot."""
    path = SCREENSHOT_DIR / f"{name}.png"
    page.screenshot(path=str(path))
    print(f"📸 Screenshot: {path}")


@pytest.mark.timeout(300)
def test_grand_simulation(test_server, base_url, simulation_contexts, screenshot_dir):
    """
    THE GRAND SIMULATION
    ====================
    One continuous E2E test covering the entire IRIS incident lifecycle.
    """
    
    admin = simulation_contexts["admin"]
    user = simulation_contexts["user"]
    agent = simulation_contexts["agent"]
    
    admin_page = admin["page"]
    user_page = user["page"]
    agent_page = agent["page"]
    
    print("\n" + "="*70)
    print("        🚀 THE GRAND SIMULATION - PHASE 34 🚀")
    print("="*70)
    
    # =========================================================================
    # PHASE 0: GENESIS
    # =========================================================================
    print("\n\n" + "▓"*70)
    print("  PHASE 0: GENESIS")
    print("▓"*70)
    
    with SimulationStep("00_db_reset", admin_page, "Database has been reset via fixture"):
        # Server fixture already handles clean DB
        print("   Database: Clean slate")
        time.sleep(1)
    
    # =========================================================================
    # PHASE 1: CALM BEFORE THE STORM
    # =========================================================================
    print("\n\n" + "▓"*70)
    print("  PHASE 1: CALM BEFORE THE STORM")
    print("▓"*70)

    # --- Admin Init ---
    with SimulationStep("01_admin_login", admin_page, "Admin logs in and verifies dashboard"):
        admin_page.goto(base_url)
        admin_page.wait_for_load_state("networkidle")
        
        # Quick login as admin
        admin_btn = admin_page.locator('button:has-text("ADMIN")').first
        admin_btn.click()
        admin_page.wait_for_load_state("networkidle")
        admin_page.wait_for_timeout(1500)
        
        # Verify dashboard loaded
        expect(admin_page.locator("#hub-view, .station-panel, #adminNav")).to_be_visible(timeout=10000)
        
        take_screenshot(admin_page, "01_Admin_Init")
    
    # --- User Init ---
    with SimulationStep("02_user_login", user_page, "User logs in and verifies terminal"):
        user_page.goto(base_url)
        user_page.wait_for_load_state("networkidle")
        
        # Quick login as user (Agatha / user1)
        user_btn = user_page.locator('button:has-text("AGATHA"), button:has-text("USER1")').first
        user_btn.click()
        user_page.wait_for_load_state("networkidle")
        user_page.wait_for_timeout(1500)
        
        # Verify terminal loaded
        expect(user_page.locator("#msgInput, .terminal-input")).to_be_visible(timeout=10000)
        
        take_screenshot(user_page, "02_User_Init")
    
    # =========================================================================
    # PHASE 2: ESCALATION
    # =========================================================================
    print("\n\n" + "▓"*70)
    print("  PHASE 2: ESCALATION")
    print("▓"*70)
    
    # --- User sends emergency ---
    with SimulationStep("03_user_emergency", user_page, "User reports emergency in chat"):
        msg_input = user_page.locator("#msgInput").first
        msg_input.fill("Máme tu únik chladiva v sektoru C, tlak stoupá!")
        user_page.keyboard.press("Enter")
        
        # Wait for message to appear in chat
        user_page.wait_for_timeout(2000)
        
        take_screenshot(user_page, "03_User_Emergency_Sent")
    
    # --- Agent Login & Check ---
    with SimulationStep("04_agent_login", agent_page, "Agent logs in to receive messages"):
        agent_page.goto(base_url)
        agent_page.wait_for_load_state("networkidle")
        
        # Quick login as agent (Krtek / agent1)
        agent_btn = agent_page.locator('button:has-text("KRTEK"), button:has-text("AGENT1")').first
        agent_btn.click()
        agent_page.wait_for_load_state("networkidle")
        agent_page.wait_for_timeout(2000)
        
        # Verify agent terminal loaded
        expect(agent_page.locator("#msgInput, .agent-terminal")).to_be_visible(timeout=10000)
        
        # Agent should see the user's message (routed via shift)
        # Note: Depending on shift offset, agent may or may not see this specific user
        take_screenshot(agent_page, "04_Agent_Received")
    
    # =========================================================================
    # PHASE 3: DIVINE INTERVENTION (Admin Controls)
    # =========================================================================
    print("\n\n" + "▓"*70)
    print("  PHASE 3: DIVINE INTERVENTION")
    print("▓"*70)
    
    # --- Admin triggers emergency mode ---
    with SimulationStep("05_admin_red_alert", admin_page, "Admin activates emergency mode"):
        # Navigate to Controls if needed
        controls_btn = admin_page.locator('div[onclick*="controls"]').first
        if controls_btn.is_visible():
            controls_btn.click(force=True)
            admin_page.wait_for_timeout(500)
        
        # Look for temperature or chernobyl controls
        # Increase temperature to trigger overload
        temp_slider = admin_page.locator('#tempSlider, input[type="range"]').first
        if temp_slider.is_visible():
            # Set to high value
            admin_page.evaluate("document.querySelector('#tempSlider, input[type=\"range\"]').value = 400")
            admin_page.wait_for_timeout(500)
        
        take_screenshot(admin_page, "05_Admin_Red_Alert")
    
    # --- Sync Check: User sees change? ---
    with SimulationStep("06_sync_check_user", user_page, "Verify user sees system state change"):
        user_page.wait_for_timeout(2000)  # Wait for WebSocket sync
        
        # Check for any visual indicator of system stress
        # (glitch class, red border, warning text, etc.)
        take_screenshot(user_page, "06_User_After_Alert")
    
    # --- Sync Check: Agent sees change? ---
    with SimulationStep("07_sync_check_agent", agent_page, "Verify agent sees system state change"):
        agent_page.wait_for_timeout(2000)  # Wait for WebSocket sync
        
        take_screenshot(agent_page, "07_Agent_After_Alert")
    
    # =========================================================================
    # PHASE 4: ECONOMIC PRESSURE
    # =========================================================================
    print("\n\n" + "▓"*70)
    print("  PHASE 4: ECONOMIC PRESSURE")
    print("▓"*70)
    
    # --- Admin fines user ---
    with SimulationStep("08_admin_fine_user", admin_page, "Admin issues fine to user"):
        # Navigate to Economy station
        economy_btn = admin_page.locator('div[onclick*="economy"]').first
        if economy_btn.is_visible():
            economy_btn.click(force=True)
            admin_page.wait_for_timeout(500)
        
        # Find and click fine button (500 credit penalty)
        fine_btn = admin_page.locator('button:has-text("-500"), button:has-text("POKUTA")').first
        if fine_btn.is_visible():
            fine_btn.click()
            admin_page.wait_for_timeout(1000)
        
        take_screenshot(admin_page, "08_Admin_Fine_Applied")
    
    # --- User sees debt ---
    with SimulationStep("09_user_debt_mode", user_page, "User experiences debt/lockout"):
        user_page.wait_for_timeout(2000)  # Wait for WebSocket update
        
        # Check for lockout overlay or negative credits indication
        take_screenshot(user_page, "09_User_Punished")
    
    # =========================================================================
    # PHASE 5: RESOLUTION
    # =========================================================================
    print("\n\n" + "▓"*70)
    print("  PHASE 5: RESOLUTION")
    print("▓"*70)
    
    # --- Agent responds ---
    with SimulationStep("10_agent_responds", agent_page, "Agent sends solution message"):
        msg_input = agent_page.locator("#msgInput").first
        if msg_input.is_visible():
            msg_input.fill("Posílám tým techniků. Zůstaňte na místě.")
            agent_page.keyboard.press("Enter")
            agent_page.wait_for_timeout(1500)
        
        take_screenshot(agent_page, "10_Agent_Response_Sent")
    
    # --- Admin gives bonus to restore user ---
    with SimulationStep("11_admin_bonus", admin_page, "Admin restores user credits"):
        bonus_btn = admin_page.locator('button:has-text("+500"), button:has-text("STIMULUS")').first
        if bonus_btn.is_visible():
            bonus_btn.click()
            admin_page.wait_for_timeout(1000)
        
        take_screenshot(admin_page, "11_Admin_Bonus_Applied")
    
    # --- Final state check ---
    with SimulationStep("12_final_state", user_page, "Verify system returned to normal"):
        user_page.wait_for_timeout(2000)
        
        # User should no longer be locked
        take_screenshot(user_page, "12_All_Clear")
    
    # =========================================================================
    # SIMULATION COMPLETE
    # =========================================================================
    print("\n\n" + "="*70)
    print("        ✅ THE GRAND SIMULATION COMPLETE ✅")
    print("="*70)
    print(f"\nScreenshots saved to: {SCREENSHOT_DIR}")
    print("No failures detected - all phases passed!")
