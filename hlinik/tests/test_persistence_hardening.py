import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os
import json
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.logic.gamestate import GameState, gamestate

class TestPersistenceHardening(unittest.TestCase):
    
    def setUp(self):
        # Reset gamestate for clean test
        gamestate.reset_state()
        
    def test_persistence_logic(self):
        """Task 4.1: Test State Persistence Export/Import"""
        print("\n--- Testing Persistence ---")
        
        # 1. Modify State
        gamestate.temperature = 500.0
        gamestate.treasury_balance = 9999
        gamestate.is_overloaded = True
        gamestate.power_load = 42.0
        gamestate.optimizer_active = True
        
        # 2. Export
        data = gamestate.export_state()
        print(f"Exported Data: {data}")
        
        # 3. Create Fresh Instance (simulating restart)
        new_gs = GameState()
        new_gs.reset_state() # Ensure it's fresh
        
        # Verify it's clean (singleton caveat: we are using the same object in memory normally, 
        # but reset_state clears it. Let's rely on import overriding reset values)
        self.assertEqual(new_gs.temperature, 80.0)
        self.assertFalse(new_gs.optimizer_active)
        
        # 4. Import
        new_gs.import_state(data)
        
        # 5. Assert
        self.assertEqual(new_gs.temperature, 500.0)
        self.assertEqual(new_gs.treasury_balance, 9999)
        self.assertTrue(new_gs.is_overloaded)
        self.assertEqual(new_gs.power_load, 42.0)
        self.assertTrue(new_gs.optimizer_active)
        print("✅ Persistence Verified")

class TestLoopResilience(unittest.IsolatedAsyncioTestCase):
    
    async def test_game_loop_resilience(self):
        """Task 4.2: Test Main Loop Resilience to Exceptions"""
        print("\n--- Testing Loop Resilience ---")
        
        # Import local
        from app.main import game_loop
        print(f"DEBUG: test gamestate id: {id(gamestate)}")
        
        # Mock GameState.process_tick
        original_tick = gamestate.process_tick
        tick_counter = {"count": 0}
        
        def exploding_tick():
            tick_counter["count"] += 1
            if tick_counter["count"] == 1:
                print("💣 BOOM! Simulate critical error.")
                raise ValueError("Simulated Explosion")
            return original_tick()
            
        # Patch the gamestate instance
        with patch.object(gamestate, 'process_tick', side_effect=exploding_tick):
            original_sleep = asyncio.sleep
            
            async def fast_sleep(delay, *args, **kwargs):
                if delay <= 0.1:
                    await original_sleep(delay)
                else:
                     # YIELD control so background task runs!
                    await original_sleep(0)
                    return # Skip long sleeps

            # Patch asyncio.sleep globally
            with patch('asyncio.sleep', side_effect=fast_sleep):
                # Start game_loop as task
                task = asyncio.create_task(game_loop())
                
                try:
                    # Let it run - use ORIGINAL sleep to wait real time!
                    await original_sleep(0.5)
                    
                    print(f"Ticks processed: {tick_counter['count']}")
                    self.assertGreater(tick_counter['count'], 1, "Loop should recover and continue ticking")
                finally:
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
        
        print("✅ Loop Resilience Verified")

if __name__ == '__main__':
    unittest.main()
