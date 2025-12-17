import json
from ..database import SessionLocal, ChatLog, User, UserRole, SystemLog
from ..logic.routing import routing_logic
from ..logic.gamestate import gamestate
from ..logic.llm_core import llm_service
from ..config import settings
from fastapi import WebSocket

PANIC_PROMPT_FALLBACK = "Panický režim nahrazuje odpověď."
PANIC_RESPONSE_FALLBACK = "PANICKÝ MÓD: Odpověď nahrazena."
PANIC_USER_FALLBACK = "PANICKÝ MÓD: Zpráva nahrazena."

def get_latest_user_message(db_session, session_id: int):
    try:
        return db_session.query(ChatLog).filter(ChatLog.session_id == session_id).order_by(ChatLog.timestamp.desc()).first()
    except Exception:
        return None

class ChatService:
    def _get_logical_id(self, username: str, role: str) -> int:
        import re
        match = re.search(r'\d+', username)
        if match:
            return int(match.group())
        return 0

    async def handle_agent_message(self, db: SessionLocal, user: User, msg_data: dict, websocket: WebSocket):
        cmd_type = msg_data.get("type")
        agent_logical_id = self._get_logical_id(user.username, "agent")

        if cmd_type == "autopilot_toggle":
            status = msg_data.get("status") # true/false
            routing_logic.active_autopilots[agent_logical_id] = status
            if not status:
                    # Clear history on OFF
                    routing_logic.hyper_histories[agent_logical_id] = []
            return

        if cmd_type == "typing_sync":
            content = msg_data.get("content", "")
            await routing_logic.broadcast_to_agent(user.id, json.dumps({
                "type": "typing_sync",
                "sender": user.username,
                "content": content
            }), exclude_ws=websocket)
            return

        content = msg_data.get("content")
        if not content: return

        shift = gamestate.global_shift_offset
        total = settings.TOTAL_SESSIONS
        agent_index = agent_logical_id - 1
        session_index = (agent_index + shift) % total
        session_id = session_index + 1

        # Ensure session tracking exists even if user prompt was not recorded yet
        if session_id not in routing_logic.pending_responses:
            routing_logic.start_pending_response(session_id)

        # Check if session has timed out - agent can no longer respond
        if routing_logic.is_session_timed_out(session_id):
            await websocket.send_text(json.dumps({
                "type": "error",
                "msg": "Odpověď vypršela. Čekejte na novou zprávu od uživatele."
            }))
            return

        # v1.5 AI Optimizer && v2.0 Confirm Flow
        final_content = content
        was_rewritten = False
        panic_state = routing_logic.get_panic_state(session_id)

        is_confirming = msg_data.get("confirm_opt", False) # Flag sent by client

        # Panic mode for agent: override outgoing content with censorship LLM
        if panic_state.get("agent"):
            prompt_source = routing_logic.get_last_user_message(session_id)
            if not prompt_source:
                latest_user = get_latest_user_message(db, session_id)
                if latest_user and latest_user.sender and latest_user.sender.role == UserRole.USER and latest_user.content:
                    prompt_source = latest_user.content
                    routing_logic.set_last_user_message(session_id, prompt_source)
            if not prompt_source:
                prompt_source = content
            final_content = await llm_service.generate_response(
                gamestate.llm_config_censor,
                [{"role": "user", "content": prompt_source or PANIC_PROMPT_FALLBACK}]
            ) or PANIC_RESPONSE_FALLBACK
            was_rewritten = True
        elif gamestate.optimizer_active and not is_confirming:
            # Check Power
            current_load = gamestate.power_load
            cost = gamestate.COST_OPTIMIZER_ACTIVE
            if current_load + cost <= gamestate.power_capacity:
                # ACTIVE and POWER OK

                # Broadcast Start
                await routing_logic.broadcast_to_session(session_id, json.dumps({
                    "type": "optimizing_start"
                }))

                if settings.OPENROUTER_API_KEY or settings.OPENAI_API_KEY or settings.GEMINI_API_KEY:
                    try:
                        rewritten = await llm_service.rewrite_message(
                            content,
                            gamestate.optimizer_prompt,
                            gamestate.llm_config_optimizer
                        ) or content
                    except Exception as e:
                        print(f"Optimizer Error: {e}")
                        rewritten = content
                else:
                    rewritten = content

                rewritten = rewritten.strip() if rewritten else content

                # v2.0: Send PREVIEW to Agent, do not broadcast/save yet
                await websocket.send_text(json.dumps({
                    "type": "optimizer_preview",
                    "original": content,
                    "rewritten": rewritten
                }))
                return # Stop processing, wait for confirmation
        
        # Save (Rewritten or Original)
        # If is_confirming, 'content' IS the rewritten version sent back by client
        log = ChatLog(session_id=session_id, sender_id=user.id, content=final_content, is_optimized=is_confirming or was_rewritten)
        db.add(log)
        db.commit()

        # Agent responded - clear pending response timer
        routing_logic.clear_pending_response(session_id)

        # Broadcast to Session (User sees final_content)
        exclude_target = None if is_confirming else websocket
        await routing_logic.broadcast_to_session(session_id, json.dumps({
            "sender": user.username,
            "role": "agent",
            "content": final_content,
            "session_id": session_id,
            "id": log.id,
            "is_optimized": log.is_optimized,  # PHASE 27: Report immunity flag
            "panic": panic_state.get("agent", False)
        }), exclude_ws=exclude_target)

    async def handle_user_message(self, db: SessionLocal, user: User, msg_data: dict, websocket: WebSocket):
        cmd_type = msg_data.get("type")
        content = msg_data.get("content")

        # Generic Action Handling (v1.9)
        if cmd_type == "action":
            action = msg_data.get("action")
            if action == "heat_tick":
                gamestate.manual_heat()
                await routing_logic.broadcast_global(json.dumps({
                    "type": "gamestate_update", 
                    "temperature": gamestate.temperature
                }))
                return

        # User Mirroring
        if cmd_type == "typing_sync":
            content = msg_data.get("content", "")
            # Send to ALL sessions of this user (including other open tabs)
            if user.id in routing_logic.user_connections:
                for conn in routing_logic.user_connections[user.id]:
                    if conn != websocket: # Don't echo back
                        await conn.send_text(json.dumps({
                            "type": "typing_sync",
                            "sender": user.username,
                            "content": content
                        }))
            return

        # v1.7 Report Logic
        if cmd_type == "report_message":
            msg_id = msg_data.get("id")
            # Verify DB
            target_log = db.query(ChatLog).filter(ChatLog.id == msg_id).first()
            if target_log:
                if target_log.is_optimized:
                    # IMMUNITY
                    await websocket.send_text(json.dumps({
                        "type": "report_denied",
                        "reason": "SYSTEM_VERIFIED"
                    }))
                else:
                    # Normal Report -> Heat Up
                    gamestate.report_anomaly()
                    target_log.was_reported = True
                    db.commit()
                    
                    # Broadcast new temp
                    await routing_logic.broadcast_global(json.dumps({
                        "type": "gamestate_update", 
                        "temperature": gamestate.temperature
                    }))
                    
                    # Ack
                    await websocket.send_text(json.dumps({
                        "type": "report_accepted",
                        "msg": "Report filed. Anomaly detected."
                    }))
                    
                    # Log
                    db_log = SessionLocal()
                    db_log.add(SystemLog(event_type="REPORT", message=f"{user.username} reported message {msg_id}"))
                    db_log.commit()
                    db_log.close()
            return

        if not content: return
        
        # Purgatory Mode Check: Fetch fresh status
        db.refresh(user) # Check if this is safer than new query
        # Actually user passed in might be detached or simple object from get_user_from_token
        # It's better to query fresh
        db_user_check = db.query(User).filter(User.id == user.id).first()
        is_purgatory = db_user_check.is_locked if db_user_check else False
        
        if is_purgatory:
            # Block Chat - Allow only tasks (handled above)
            # Optionally send error back
            await websocket.send_text(json.dumps({
               "type": "error",
               "msg": "COMMUNICATION OFFLINE due to Debt."
            }))
            return

        session_id = self._get_logical_id(user.username, "user")
        panic_state = routing_logic.get_panic_state(session_id)
        if panic_state.get("user"):
            censored = await llm_service.generate_response(
                gamestate.llm_config_censor,
                [{"role": "user", "content": content}]
            )
            content = censored or PANIC_USER_FALLBACK
        routing_logic.set_last_user_message(session_id, content)
        # Save User Message
        log = ChatLog(session_id=session_id, sender_id=user.id, content=content)
        db.add(log)
        db.commit()
        
        # Clear any previous timeout and start pending response timer
        routing_logic.clear_session_timeout(session_id)
        routing_logic.start_pending_response(session_id)
        
        await routing_logic.broadcast_to_session(session_id, json.dumps({
            "sender": user.username,
            "role": "user",
            "content": content,
            "id": log.id,
            "panic": panic_state.get("user", False)
        }), exclude_ws=websocket)
        
        # CHECK FOR AUTOPILOT
        # Reverse Routing: Which Agent is on this Session?
        shift = gamestate.global_shift_offset
        total = settings.TOTAL_SESSIONS
        agent_index = (session_id - 1 - shift) % total
        agent_logical_id = agent_index + 1 # This is the Agent mapped to this user
        
        if routing_logic.active_autopilots.get(agent_logical_id):
            await routing_logic.broadcast_to_session(session_id, json.dumps({
                "type": "optimizing_start",
                "mode": "hyper"
            }))
            # 1. Update History
            if agent_logical_id not in routing_logic.hyper_histories:
                routing_logic.hyper_histories[agent_logical_id] = []
            
            history = routing_logic.hyper_histories[agent_logical_id]
            history.append({"role": "user", "content": content})
            
            # 2. Generate Reply
            try:
                reply = await llm_service.generate_response(gamestate.llm_config_hyper, history)
            except Exception as e:
                print(f"Autopilot Error: {e}")
                reply = "..."

            # 3. Add Reply to History
            history.append({"role": "assistant", "content": reply})
            
            # 4. Save & Broadcast (As Agent)
            agent_username = f"agent{agent_logical_id}"
            agent_db_user = db.query(User).filter(User.username == agent_username).first()
            
            if agent_db_user and reply:
                log_ai = ChatLog(session_id=session_id, sender_id=agent_db_user.id, content=reply)
                db.add(log_ai)
                db.commit()
                
                # Autopilot responded - clear pending response timer
                routing_logic.clear_pending_response(session_id)
                
                await routing_logic.broadcast_to_session(session_id, json.dumps({
                    "sender": agent_username,
                    "role": "agent",
                    "content": reply,
                    "session_id": session_id,
                    "id": log_ai.id
                }))

    async def handle_typing_indicator(self, user: User, msg_data: dict, websocket: WebSocket):
        msg_type = msg_data.get("type")
        if msg_type in ["typing_start", "typing_stop"]:
            if user.role == UserRole.USER:
                # Value from User -> Send to Agent
                session_id = self._get_logical_id(user.username, "user")
                await routing_logic.broadcast_to_session(session_id, json.dumps({
                    "type": msg_type,
                    "sender": user.username,
                    "role": "user",
                    "session_id": session_id
                }), exclude_ws=websocket)
                
            elif user.role == UserRole.AGENT:
                # Agent typing -> Send to User in current session
                target_session_id = self._get_logical_id(user.username, "agent")
                
                if target_session_id:
                    await routing_logic.broadcast_to_session(target_session_id, json.dumps({
                        "type": msg_type,
                        "sender": user.username,
                        "role": "agent",
                        "session_id": target_session_id
                    }), exclude_ws=websocket)

