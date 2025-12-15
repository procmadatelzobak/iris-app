"""
SIMULATION API ROUTER
======================
IRIS 4.0 - Phase 35

API endpoints pro spouštění a monitorování LLM hodinové simulace.
Přístupné pouze pro ROOT uživatele.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
import asyncio
import sys
from pathlib import Path

from ..dependencies import get_current_root

# Add tests to path for importing simulation module
_tests_path = Path(__file__).resolve().parent.parent.parent / "tests" / "scenarios"
if str(_tests_path.parent) not in sys.path:
    sys.path.insert(0, str(_tests_path.parent.parent))

try:
    from tests.scenarios.llm_hour_simulation import get_simulation, SimulationState
except ImportError:
    # Fallback: Define minimal stubs if import fails
    from enum import Enum
    class SimulationState(str, Enum):
        IDLE = "idle"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
    
    _simulation_instance = None
    def get_simulation():
        raise HTTPException(status_code=500, detail="Simulation module not available")

router = APIRouter(prefix="/api/admin/simulation", tags=["simulation"])


class SimulationStartRequest(BaseModel):
    """Request pro spuštění simulace"""
    short_test: bool = False  # Krátký 5-minutový test místo 1 hodiny


class SimulationResponse(BaseModel):
    """Response se stavem simulace"""
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None


@router.get("/status")
async def get_simulation_status(admin=Depends(get_current_root)) -> Dict[str, Any]:
    """
    ROOT ONLY: Získá aktuální stav simulace.
    
    Returns:
        - state: idle/running/paused/stopping/completed/failed
        - elapsed_seconds: Uplynulý čas v sekundách
        - remaining_seconds: Zbývající čas v sekundách
        - progress_percent: Procento dokončení
        - participants_count: Počet účastníků
        - config: Konfigurace simulace
        - summary: Souhrn (pokud běží nebo skončila)
    """
    sim = get_simulation()
    return sim.get_status()


@router.post("/start")
async def start_simulation(
    request: SimulationStartRequest,
    background_tasks: BackgroundTasks,
    admin=Depends(get_current_root)
) -> SimulationResponse:
    """
    ROOT ONLY: Spustí LLM hodinovou simulaci.
    
    Simulace běží na pozadí a lze ji monitorovat přes /status endpoint.
    
    Args:
        short_test: Pokud true, spustí 5-minutový test místo 1 hodiny
        
    Returns:
        - status: "started" nebo "error"
        - message: Popis výsledku
        - data: Aktuální stav simulace
    """
    sim = get_simulation()
    
    if sim.state == SimulationState.RUNNING:
        return SimulationResponse(
            status="error",
            message="Simulace již běží. Počkejte na dokončení nebo ji zastavte.",
            data=sim.get_status()
        )
    
    # Start simulation
    success = await sim.start(short_test=request.short_test)
    
    if not success:
        return SimulationResponse(
            status="error",
            message="Nepodařilo se spustit simulaci. Zkontrolujte logy.",
            data=sim.get_status()
        )
    
    mode = "SHORT TEST (5 min)" if request.short_test else "FULL (1 hour)"
    return SimulationResponse(
        status="started",
        message=f"Simulace spuštěna v režimu {mode}",
        data=sim.get_status()
    )


@router.post("/stop")
async def stop_simulation(admin=Depends(get_current_root)) -> SimulationResponse:
    """
    ROOT ONLY: Zastaví běžící simulaci.
    
    Simulace dokončí aktuální cyklus a poté se ukončí.
    Výsledky budou uloženy do lore-web.
    
    Returns:
        - status: "stopping" nebo "error"
        - message: Popis výsledku
        - data: Aktuální stav simulace
    """
    sim = get_simulation()
    
    if sim.state != SimulationState.RUNNING:
        return SimulationResponse(
            status="error",
            message=f"Simulace neběží. Aktuální stav: {sim.state.value}",
            data=sim.get_status()
        )
    
    success = await sim.stop()
    
    if not success:
        return SimulationResponse(
            status="error",
            message="Nepodařilo se zastavit simulaci.",
            data=sim.get_status()
        )
    
    return SimulationResponse(
        status="stopping",
        message="Zastavuji simulaci... Dokončuji aktuální cyklus.",
        data=sim.get_status()
    )


@router.get("/logs")
async def get_simulation_logs(
    limit: int = 100,
    admin=Depends(get_current_root)
) -> Dict[str, Any]:
    """
    ROOT ONLY: Získá logy z aktuální/poslední simulace.
    
    Args:
        limit: Maximální počet logů (výchozí 100)
        
    Returns:
        - logs: Seznam logů
        - errors: Seznam chyb
        - stats: Statistiky
    """
    sim = get_simulation()
    
    if sim.logger is None:
        return {
            "logs": [],
            "errors": [],
            "stats": None,
            "message": "Žádná simulace nebyla spuštěna"
        }
    
    logs = sim.logger.logs[-limit:] if len(sim.logger.logs) > limit else sim.logger.logs
    
    return {
        "logs": logs,
        "errors": sim.logger.errors,
        "stats": sim.logger.stats.to_dict() if sim.logger.stats else None
    }


@router.get("/history")
async def get_simulation_history(
    limit: int = 20,
    admin=Depends(get_current_root)
) -> Dict[str, Any]:
    """
    ROOT ONLY: Získá historii předchozích simulací z lore-web.
    
    Args:
        limit: Maximální počet záznamů (výchozí 20)
        
    Returns:
        - runs: Seznam předchozích běhů
    """
    import json
    from pathlib import Path
    
    # Path to index.json
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    index_file = base_dir / "doc" / "iris" / "lore-web" / "data" / "test_runs" / "index.json"
    
    if not index_file.exists():
        return {"runs": [], "message": "Žádné předchozí simulace"}
    
    try:
        with open(index_file, "r", encoding="utf-8") as f:
            runs = json.load(f)
        
        # Filter only LLM simulations and sort by timestamp
        llm_runs = [r for r in runs if "LLM" in r.get("scenario_name", "")]
        llm_runs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {"runs": llm_runs[:limit]}
        
    except Exception as e:
        return {"runs": [], "error": str(e)}
