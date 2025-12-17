from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import os
from .routers import auth, sockets, admin_api, translations, docs, simulation, lore_editor_api
from .database import init_db
from .config import settings, BASE_DIR
from .seed import seed_data
import asyncio
import traceback
import json
import time

async def game_loop():
    last_val = -1
    last_load = -1
    last_treasury = -1
    last_overload = False
    
    from .logic.gamestate import gamestate
    from .logic.routing import routing_logic

    while True:
        try:
            await asyncio.sleep(1)
            
            # 0. Check for agent response timeouts
            current_time = time.time()
            timeout_window = gamestate.agent_response_window
            
            # Copy keys to avoid modification during iteration
            pending_sessions = list(routing_logic.pending_responses.keys())
            for session_id in pending_sessions:
                start_time = routing_logic.pending_responses.get(session_id)
                if start_time and (current_time - start_time) >= timeout_window:
                    # Timeout occurred - send error to user and block agent
                    await routing_logic.send_timeout_error_to_user(session_id)
                    await routing_logic.send_timeout_to_agent(session_id)
                    routing_logic.mark_session_timeout(session_id)
            
            # 1. Tick Chernobyl
            new_val = gamestate.process_tick()
            
            # 2. Calc Load
            counts = routing_logic.get_active_counts()
            is_low_latency = gamestate.agent_response_window <= 30
            current_load = gamestate.calc_load(
                active_terminals=counts["users"],
                active_autopilots=counts["autopilots"],
                low_latency_active=is_low_latency
            )
            
            # 3. Check Overload
            overload_events = gamestate.check_overload()
            current_is_overloaded = gamestate.is_overloaded

            # Process Panic Mode (moved from gamestate)
            if "panic_trigger" in overload_events:
                should_panic = overload_events["panic_trigger"]
                # Safe to call routing here
                total_sessions = getattr(settings, "TOTAL_SESSIONS", 8) # Fallback to 8 if generic
                # Or just settings.TOTAL_SESSIONS as imported
                total_sessions = settings.TOTAL_SESSIONS
                
                for i in range(1, total_sessions + 1):
                    routing_logic.set_panic_mode(i, "user", should_panic)
                    routing_logic.set_panic_mode(i, "agent", should_panic)
                
                # Send special panic update
                await routing_logic.broadcast_global(json.dumps({
                    "type": "gamestate_update",
                    "panic_global": should_panic,
                    "temperature": gamestate.temperature,
                    "is_overloaded": current_is_overloaded
                }))
            
            # 4. Broadcast
            # Detect changes (Optimization: only send if changed)
            if (int(new_val) != int(last_val) or 
                current_load != last_load or 
                gamestate.treasury_balance != last_treasury or
                current_is_overloaded != last_overload):
                
                await routing_logic.broadcast_global(json.dumps({
                    "type": "gamestate_update",
                    "temperature": new_val,
                    "shift": gamestate.global_shift_offset,
                    "power_load": current_load,
                    "power_capacity": gamestate.power_capacity,
                    "treasury": gamestate.treasury_balance,
                    "is_overloaded": current_is_overloaded,
                    "agent_window": gamestate.agent_response_window,
                    "hyper_mode": gamestate.hyper_visibility_mode.value
                }))
                
                last_val = new_val
                last_load = current_load
                last_treasury = gamestate.treasury_balance
                last_overload = current_is_overloaded
                
        except asyncio.CancelledError:
            # Handle cancellation gracefully
            break
        except Exception as e:
            print(f"CRITICAL ERROR IN GAME LOOP: {e}")
            traceback.print_exc()
            await asyncio.sleep(5)  # Pause before retrying to prevent log flood
            continue

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    seed_data()
    
    # --- STATE PERSISTENCE: Load on Startup ---
    from pathlib import Path
    from .logic.gamestate import gamestate
    from .logic.routing import routing_logic
    
    data_dir = BASE_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    state_file = data_dir / "gamestate.json"
    
    if state_file.exists():
        try:
            with open(state_file, "r") as f:
                state_data = json.load(f)
            gamestate.import_state(state_data)
            print("System state restored from persistence.")
        except Exception as e:
            print(f"WARN: Could not restore GameState: {e}")
    else:
        print("No persistence file found. Starting with fresh state.")
    
    # Background Task
    task = asyncio.create_task(game_loop())
    yield
    
    # --- STATE PERSISTENCE: Save on Shutdown ---
    task.cancel()
    try:
        state_data = gamestate.export_state()
        with open(state_file, "w") as f:
            json.dump(state_data, f, indent=2)
        print("System state saved to persistence.")
    except Exception as e:
        print(f"ERROR: Could not save GameState: {e}")

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION, lifespan=lifespan)

# Static Files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
lore_web_dir = BASE_DIR.parent / "doc" / "iris" / "lore-web"

if lore_web_dir.exists():
    # Phase 34: Consolidated Lore Web
    app.mount("/lore-web", StaticFiles(directory=str(lore_web_dir), html=True), name="lore-web")
    app.mount("/organizer-wiki", StaticFiles(directory=str(lore_web_dir), html=True), name="wiki")

app.mount("/docs/images", StaticFiles(directory=BASE_DIR / "docs" / "images"), name="docs_images")

# Templates
templates = Jinja2Templates(directory=BASE_DIR / "app" / "templates")

# Routers
app.include_router(auth.router)
app.include_router(sockets.router)
app.include_router(admin_api.router)
app.include_router(translations.router)
app.include_router(docs.router)
app.include_router(simulation.router)
app.include_router(lore_editor_api.router)

@app.get("/health")
async def health():
    version = getattr(settings, "VERSION", None) or "unknown"
    return {"status": "ok", "version": version}

@app.get("/")
async def root(request: Request):
    # Test Mode Logic
    from .logic.gamestate import gamestate
    from .database import SessionLocal, User
    
    users = []
    if gamestate.test_mode:
        db = SessionLocal()
        users = db.query(User).order_by(User.role, User.username).all()
        db.close()
        
    return templates.TemplateResponse("login.html", {
        "request": request, 
        "title": "IRIS Login",
        "test_mode": gamestate.test_mode,
        "users": users
    })
