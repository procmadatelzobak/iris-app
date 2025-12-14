"""
IRIS Translation System

This module provides utilities for loading and managing translations.
Future implementation will include:
- Translation loading from JSON files
- Language switching logic
- Custom admin label management
- Real-time translation updates via WebSocket
"""

import json
from pathlib import Path
from typing import Dict, Optional

# Translation cache
_translations_cache: Dict[str, dict] = {}

def load_translations(language: str = "czech") -> dict:
    """
    Load translation file from disk.
    
    Args:
        language: Language code ("czech" or "iris")
    
    Returns:
        Dictionary with translations
    """
    if language in _translations_cache:
        return _translations_cache[language]
    
    translations_dir = Path(__file__).parent
    file_path = translations_dir / f"{language}.json"
    
    if not file_path.exists():
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        translations = json.load(f)
    
    _translations_cache[language] = translations
    return translations


def get_translation(key_path: str, language_mode: str = "cz", custom_labels: Optional[dict] = None) -> str:
    """
    Get translation for a given key path with priority handling.
    
    Priority:
    1. Custom admin labels (highest)
    2. Language-specific translation
    3. Fallback to key_path itself
    
    Args:
        key_path: Dot-separated key path (e.g., "login.username_label")
        language_mode: "cz" for czech, "czech-iris" for IRIS mode
        custom_labels: Dict of custom admin overrides from database
    
    Returns:
        Translated string
    
    Example:
        >>> get_translation("login.username_label", "cz")
        "IDENTIFIKÁTOR"
    """
    # Priority 1: Check custom admin override
    if custom_labels and key_path in custom_labels:
        return custom_labels[key_path]
    
    # Priority 2: Load appropriate language file(s)
    if language_mode == "czech-iris":
        # Try IRIS first, fallback to czech
        iris_trans = load_translations("iris")
        czech_trans = load_translations("czech")
        
        # Navigate through nested keys
        value = _get_nested_value(iris_trans, key_path)
        if value is None:
            value = _get_nested_value(czech_trans, key_path)
    else:  # default "cz"
        czech_trans = load_translations("czech")
        value = _get_nested_value(czech_trans, key_path)
    
    # Priority 3: Fallback to key path itself
    return value if value is not None else key_path


def _get_nested_value(data: dict, key_path: str) -> Optional[str]:
    """
    Get value from nested dictionary using dot-separated path.
    
    Args:
        data: Dictionary to search
        key_path: Dot-separated key path
    
    Returns:
        Value if found, None otherwise
    """
    keys = key_path.split('.')
    current = data
    
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    
    return current if isinstance(current, str) else None


def merge_translations(base: dict, override: dict) -> dict:
    """
    Deep merge two translation dictionaries.
    Override values take precedence over base values.
    
    Args:
        base: Base translation dictionary
        override: Override translation dictionary
    
    Returns:
        Merged dictionary
    """
    result = base.copy()
    
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_translations(result[key], value)
        else:
            result[key] = value
    
    return result


def clear_cache():
    """Clear translation cache. Useful for hot-reloading."""
    global _translations_cache
    _translations_cache = {}


# TODO: Add database integration for custom labels
# - Create CustomLabel model with key/value fields
# - Add CRUD operations for custom labels
# - Integrate with get_translation() function
#
# TODO: Add WebSocket broadcast for real-time updates
# - Implement broadcast_translation_update(key, value)
# - Implement broadcast_language_change(language_mode)
# - Implement broadcast_translation_reset()
#
# TODO: Add validation of translation keys against HTML templates
# - Parse HTML templates for data-key attributes
# - Compare against available translation keys
# - Generate report of missing translations
