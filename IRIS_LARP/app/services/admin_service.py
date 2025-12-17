import json
import os
from ..database import SessionLocal, SystemLog, User
from ..logic.routing import routing_logic
from ..logic.gamestate import gamestate
from ..config import settings
from fastapi import WebSocket

class AdminService:
    async def handle_admin_command(self, db: SessionLocal, user: User, msg_data: dict, websocket: WebSocket):
        cmd_type = msg_data.get("type")
        
        if cmd_type == "action":
            action = msg_data.get("action")
            if action == "heat_tick":
                gamestate.manual_heat()
                await routing_logic.broadcast_global(json.dumps({
                    "type": "gamestate_update", 
                    "temperature": gamestate.temperature
                }))
                return

        if cmd_type == "shift_command":
            new_shift = gamestate.increment_shift()
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update", 
                "shift": new_shift,
                "temperature": gamestate.temperature
            }))
        
        elif cmd_type == "set_shift_command":
            target = msg_data.get("value", 0)
            new_shift = gamestate.set_shift(int(target))
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update", 
                "shift": new_shift,
                "temperature": gamestate.temperature
            }))
        
        elif cmd_type == "temperature_command": 
            level = msg_data.get("value", 0) 
            gamestate.set_temperature(float(level))
            
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update", 
                "shift": gamestate.global_shift_offset,
                "temperature": gamestate.temperature
            }))

        elif cmd_type == "chernobyl_mode_command":
            from ..logic.gamestate import ChernobylMode
            mode_str = msg_data.get("mode", "normal")
            # Map string to enum
            if mode_str == "low_power":
                gamestate.chernobyl_mode = ChernobylMode.LOW_POWER
            elif mode_str == "overclock":
                gamestate.chernobyl_mode = ChernobylMode.OVERCLOCK
            else:
                gamestate.chernobyl_mode = ChernobylMode.NORMAL
            
            # Broadcast update
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update", 
                "chernobyl_mode": gamestate.chernobyl_mode.value
            }))

        elif cmd_type == "reset_game":
            from ..logic.gamestate import ChernobylMode, HyperVisibilityMode
            
            # Soft Reset: Broadcast failover message, reset temp/labels, keep credits/power
            gamestate.set_temperature(gamestate.TEMP_RESET_VALUE)
            gamestate.chernobyl_mode = ChernobylMode.NORMAL
            gamestate.hyper_visibility_mode = HyperVisibilityMode.NORMAL
            
            # Reset custom labels (delete admin_labels.json)
            # Better way: config.BASE_DIR
            from ..config import BASE_DIR
            labels_path = BASE_DIR / "data" / "admin_labels.json"

            if os.path.exists(labels_path):
                os.remove(labels_path)
            
            # Reset GameState Dicts
            gamestate.panic_modes = {}
            gamestate.latest_user_messages = {}
            
            # Broadcast failover message to ALL users
            await routing_logic.broadcast_global(json.dumps({
                "type": "system_alert",
                "content": "⚠️ SYSTÉM REINICIALIZOVÁN ⚠️\nDošlo k přepnutí na záložní server v rámci failover protokolu.\nVšechny relace byly obnoveny. Pokračujte v práci.",
                "alert_type": "failover"
            }))
            
            # Also send gamestate update
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update", 
                "shift": gamestate.global_shift_offset,
                "temperature": gamestate.temperature,
                "hyper_mode": "normal",
                "is_overloaded": False
            }))
            
        elif cmd_type == "admin_broadcast":
                content = msg_data.get("content", "SYSTEM ALERT")
                await routing_logic.broadcast_global(json.dumps({
                    "type": "message",
                    "sender": "ROOT",
                    "role": "admin",
                    "content": f"⚠ {content} ⚠",
                    "is_alert": True
                }))

        elif cmd_type == "admin_view_sync":
            view = msg_data.get("view", "monitor")
            await routing_logic.broadcast_to_admins(json.dumps({
                "type": "admin_view_sync",
                "view": view,
                "sender_id": user.id 
            }))
            
        elif cmd_type == "hyper_vis_command":
            mode_str = msg_data.get("mode", "normal")
            from ..logic.gamestate import HyperVisibilityMode
            if mode_str == "normal":
                gamestate.hyper_visibility_mode = HyperVisibilityMode.NORMAL
            elif mode_str == "blackbox":
                gamestate.hyper_visibility_mode = HyperVisibilityMode.BLACKBOX
            elif mode_str == "forensic":
                gamestate.hyper_visibility_mode = HyperVisibilityMode.FORENSIC
            
            # Log
            db_log = SessionLocal()
            db_log.add(SystemLog(event_type="ACTION", message=f"{user.username} changed HYPER to {mode_str}"))
            db_log.commit()
            db_log.close()
            
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update",
                "hyper_mode": gamestate.hyper_visibility_mode.value
            }))

        elif cmd_type == "test_mode_toggle":
            enabled = msg_data.get("enabled", False)
            gamestate.test_mode = enabled
            # Broadcast status? Maybe just ack.
            await websocket.send_text(json.dumps({
                "type": "admin_ack",
                "msg": f"TEST MODE set to {enabled}"
            }))

        elif cmd_type == "panic_command":
            enabled = msg_data.get("enabled", False)
            # Global Panic set for all sessions
            for i in range(1, settings.TOTAL_SESSIONS + 1):
                    gamestate.set_panic_mode(i, "user", enabled)
                    gamestate.set_panic_mode(i, "agent", enabled)
            
            await routing_logic.broadcast_global(json.dumps({
                "type": "gamestate_update",
                "panic_global": enabled
            }))
