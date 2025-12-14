"""
Translations API Router

Provides endpoints for:
- Getting all translations for current language
- Setting language mode (root only)
- Managing custom admin labels
- Resetting custom labels
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, field_validator
from typing import Dict, Optional
import html
import json
import re

from ..dependencies import get_current_admin, get_current_user
from ..logic.gamestate import gamestate
from ..translations import load_translations, merge_translations, clear_cache
from ..logic.routing import routing_logic

router = APIRouter(prefix="/api/translations", tags=["translations"])


class CustomLabelUpdate(BaseModel):
    key: str
    value: str
    
    @field_validator('key')
    @classmethod
    def validate_key(cls, v):
        # Limit key length and format
        if len(v) > 100:
            raise ValueError('Key too long (max 100 chars)')
        # Allow alphanumeric (including Unicode), underscore, dot, and hyphen
        if not re.match(r'^[\w\.\-]+$', v, re.UNICODE):
            raise ValueError('Key can only contain word characters, underscore, dot and hyphen')
        return v
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v):
        # Limit value length and sanitize
        if len(v) > 200:
            raise ValueError('Value too long (max 200 chars)')
        # Basic HTML escape
        return html.escape(v)


class LanguageModeUpdate(BaseModel):
    language_mode: str
    
    @field_validator('language_mode')
    @classmethod
    def validate_mode(cls, v):
        if v not in ["cz", "czech-iris"]:
            raise ValueError('Invalid language mode. Must be "cz" or "czech-iris"')
        return v


@router.get("/")
async def get_translations(user=Depends(get_current_user)):
    """
    Get all translations for current language mode.
    Returns merged translations with custom labels applied.
    """
    language_mode = gamestate.language_mode
    custom_labels = gamestate.custom_labels
    
    # Load base translations
    czech_trans = load_translations("czech")
    
    if language_mode == "czech-iris":
        # Load and merge IRIS overrides
        iris_trans = load_translations("iris")
        translations = merge_translations(czech_trans, iris_trans)
    else:
        translations = czech_trans
    
    return {
        "status": "ok",
        "language_mode": language_mode,
        "translations": translations,
        "custom_labels": custom_labels
    }


@router.post("/language")
async def set_language_mode(update: LanguageModeUpdate, admin=Depends(get_current_admin)):
    """
    Set system language mode (root only).
    Broadcasts change to all connected clients.
    """
    # Check if user is root
    if admin.username != "root":
        raise HTTPException(status_code=403, detail="Only root can change language mode")
    
    gamestate.language_mode = update.language_mode
    
    # Clear cache to force reload
    clear_cache()
    
    # Broadcast language change
    await routing_logic.broadcast_global(json.dumps({
        "type": "language_change",
        "language_mode": update.language_mode
    }))
    
    return {
        "status": "ok",
        "language_mode": update.language_mode
    }


@router.post("/label")
async def set_custom_label(update: CustomLabelUpdate, admin=Depends(get_current_admin)):
    """
    Set a custom label (admin only).
    Custom labels override language translations.
    """
    gamestate.custom_labels[update.key] = update.value
    
    # Broadcast label update
    await routing_logic.broadcast_global(json.dumps({
        "type": "translation_update",
        "key": update.key,
        "value": update.value
    }))
    
    return {
        "status": "ok",
        "key": update.key,
        "value": update.value
    }


@router.delete("/label/{key}")
async def delete_custom_label(key: str, admin=Depends(get_current_admin)):
    """
    Delete a custom label.
    """
    if key in gamestate.custom_labels:
        del gamestate.custom_labels[key]
        
        # Broadcast label deletion
        await routing_logic.broadcast_global(json.dumps({
            "type": "translation_update",
            "key": key,
            "value": None  # None indicates deletion
        }))
        
        return {"status": "deleted", "key": key}
    
    return {"status": "not_found", "key": key}


@router.post("/reset-labels")
async def reset_all_labels(admin=Depends(get_current_admin)):
    """
    Reset all custom labels (admin only).
    """
    gamestate.custom_labels = {}
    
    # Broadcast reset
    await routing_logic.broadcast_global(json.dumps({
        "type": "translations_reset"
    }))
    
    return {"status": "reset", "message": "All custom labels cleared"}


@router.get("/language-options")
async def get_language_options(user=Depends(get_current_user)):
    """
    Get available language options.
    """
    return {
        "status": "ok",
        "options": [
            {"value": "cz", "label": "Čeština (výchozí)"},
            {"value": "czech-iris", "label": "Čeština + IRIS Terminologie"}
        ],
        "current": gamestate.language_mode
    }
