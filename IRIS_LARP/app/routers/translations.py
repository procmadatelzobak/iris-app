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
import os

from ..dependencies import get_current_admin, get_current_user
from ..logic.gamestate import gamestate
from ..config import BASE_DIR
from ..translations import load_translations, merge_translations, clear_cache
from ..logic.routing import routing_logic

router = APIRouter(prefix="/api/translations", tags=["translations"])

TRANSLATION_FILES = {
    "cz": "czech.json",
    "crazy": "crazy.json",
    "en": "english.json",
    "iris": "iris.json"
}


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
        valid_modes = ["cz", "en", "crazy", "czech-iris"]
        if v not in valid_modes:
            raise ValueError(f'Invalid language mode. Must be one of: {", ".join(valid_modes)}')
        return v


@router.get("/")
async def get_translations(user=Depends(get_current_user)):
    """
    Get all translations for current language mode.
    Returns merged translations with custom labels applied.
    """
    language_mode = gamestate.language_mode
    custom_labels = gamestate.custom_labels
    
    # Load base translations based on language mode
    if language_mode == "en":
        translations = load_translations("english")
    elif language_mode == "crazy":
        translations = load_translations("crazy")
    elif language_mode == "czech-iris":
        # Load and merge IRIS overrides
        czech_trans = load_translations("czech")
        iris_trans = load_translations("iris")
        translations = merge_translations(czech_trans, iris_trans)
    else:  # default "cz"
        translations = load_translations("czech")
    
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
            {"value": "en", "label": "English"},
            {"value": "crazy", "label": "Crazy Čeština 🤪"},
            {"value": "czech-iris", "label": "Čeština + IRIS Terminologie"}
        ],
        "current": gamestate.language_mode
    }


@router.get("/files/list")
async def list_translation_files(user=Depends(get_current_user)):
    """
    List available translation files for editing.
    """
    return {
        "status": "ok",
        "files": [
            {"code": "cz", "name": "Čeština (czech.json)"},
            {"code": "crazy", "name": "Crazy Čeština (crazy.json)"},
            # "en" and "iris" can be added if needed, but requirements mentioned cz and crazy
        ]
    }


@router.get("/files/{code}")
async def get_translation_file_content(code: str, user=Depends(get_current_user)):
    """
    Get raw content of a translation file.
    """
    if code not in TRANSLATION_FILES:
        raise HTTPException(status_code=404, detail="File not found")
        
    filename = TRANSLATION_FILES[code]
    file_path = BASE_DIR / "app" / "translations" / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = json.load(f)
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")


@router.post("/files/{code}")
async def save_translation_file_content(code: str, content: Dict = Body(...), admin=Depends(get_current_admin)):
    """
    Save content to a translation file (ROOT/ADMIN only).
    """
    if code not in TRANSLATION_FILES:
        raise HTTPException(status_code=404, detail="File not found")
        
    filename = TRANSLATION_FILES[code]
    file_path = BASE_DIR / "app" / "translations" / filename
    
    try:
        # Validate JSON by dumping it first (although Body(...) ensures it's valid JSON)
        json_str = json.dumps(content, indent=2, ensure_ascii=False)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(json_str)
            
        # Clear cache to ensure immediate effect if this language is active
        clear_cache()
        
        # Broadcast update trigger (optional, maybe overkill to reload everything)
        
        return {"status": "saved", "file": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")
