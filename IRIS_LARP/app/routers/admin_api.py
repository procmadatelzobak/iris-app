from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from ..dependencies import get_current_admin
from ..logic.llm_core import llm_service, LLMConfig, LLMProvider
from ..logic.gamestate import gamestate

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/llm/models/{provider}")
async def list_models(provider: LLMProvider, admin=Depends(get_current_admin)):
    return llm_service.list_models(provider)

@router.get("/llm/config")
async def get_llm_config(admin=Depends(get_current_admin)):
    return {
        "task": gamestate.llm_config_task,
        "hyper": gamestate.llm_config_hyper
    }

@router.post("/llm/config/{config_type}")
async def set_llm_config(config_type: str, config: LLMConfig, admin=Depends(get_current_admin)):
    if config_type == "task":
        gamestate.llm_config_task = config
    elif config_type == "hyper":
        gamestate.llm_config_hyper = config
    else:
        raise HTTPException(status_code=400, detail="Invalid config type")
    return {"status": "ok"}

# API Key Management
from ..database import SessionLocal, SystemConfig
from pydantic import BaseModel

class KeyUpdate(BaseModel):
    provider: LLMProvider
    key: str

@router.get("/llm/keys")
async def get_keys(admin=Depends(get_current_admin)):
    db = SessionLocal()
    keys = {}
    for provider in LLMProvider:
        key_name = f"{provider.value.upper()}_API_KEY"
        config = db.query(SystemConfig).filter(SystemConfig.key == key_name).first()
        val = config.value if config else ""
        # Mask
        if val and len(val) > 8:
            keys[provider.value] = f"{val[:4]}...{val[-4:]}"
        elif val:
            keys[provider.value] = "****"
        else:
            keys[provider.value] = None
    db.close()
    return keys

@router.post("/llm/keys")
async def set_key(update: KeyUpdate, admin=Depends(get_current_admin)):
    db = SessionLocal()
    key_name = f"{update.provider.value.upper()}_API_KEY"
    config = db.query(SystemConfig).filter(SystemConfig.key == key_name).first()
    if not config:
        config = SystemConfig(key=key_name, value=update.key)
        db.add(config)
    else:
        config.value = update.key
    db.commit()
    db.close()
    return {"status": "updated", "provider": update.provider}
