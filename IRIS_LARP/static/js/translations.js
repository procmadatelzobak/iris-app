/**
 * IRIS Translation Manager
 * 
 * Provides client-side translation loading and management:
 * - Loads translations from server
 * - Applies translations to elements with data-key attributes
 * - Manages custom admin labels
 * - Handles real-time updates via WebSocket
 */

class TranslationManager {
    constructor() {
        this.translations = {};
        this.customLabels = {};
        this.languageMode = 'cz';
        this.initialized = false;
    }

    /**
     * Initialize the translation manager.
     * Fetches translations from server and applies them.
     */
    async init() {
        try {
            const token = localStorage.getItem('token') || this.getCookie('access_token');
            const response = await fetch('/api/translations/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (!response.ok) {
                console.warn('Failed to load translations:', response.status);
                return;
            }
            
            const data = await response.json();
            
            this.translations = data.translations || {};
            this.customLabels = data.custom_labels || {};
            this.languageMode = data.language_mode || 'cz';
            this.initialized = true;
            
            // Apply translations to UI
            this.updateAllLabels();
            
            console.log('TranslationManager initialized:', this.languageMode);
        } catch (e) {
            console.error('TranslationManager init failed:', e);
        }
    }

    /**
     * Get cookie value by name
     */
    getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            let val = parts.pop().split(';').shift();
            if (val && val.startsWith('"')) val = val.slice(1, -1);
            return val;
        }
        return null;
    }

    /**
     * Get translation for a given key path.
     * Priority: custom labels > language translations > key path itself
     */
    get(keyPath) {
        // Priority 1: Check custom admin override
        if (this.customLabels[keyPath]) {
            return this.customLabels[keyPath];
        }
        
        // Priority 2: Navigate through translations
        const value = this.getNestedValue(keyPath);
        
        // Priority 3: Return key path as fallback
        return value || keyPath;
    }

    /**
     * Navigate nested object using dot-separated path
     */
    getNestedValue(keyPath) {
        const keys = keyPath.split('.');
        let current = this.translations;
        
        for (const key of keys) {
            if (!current || typeof current !== 'object') return null;
            current = current[key];
        }
        
        return typeof current === 'string' ? current : null;
    }

    /**
     * Update all labels in the DOM with translations
     */
    updateAllLabels() {
        document.querySelectorAll('[data-key]').forEach(el => {
            const key = el.getAttribute('data-key');
            const translation = this.get(key);
            
            // Update text content
            if (translation && translation !== key) {
                // Check if element has only text content
                if (el.childNodes.length === 1 && el.childNodes[0].nodeType === Node.TEXT_NODE) {
                    el.textContent = translation;
                } else if (el.childNodes.length === 0) {
                    el.textContent = translation;
                } else {
                    // For complex elements, update first text node
                    this.updateTextNode(el, translation);
                }
            }
        });
    }

    /**
     * Update first text node in element
     */
    updateTextNode(element, newText) {
        for (let node of element.childNodes) {
            if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                node.textContent = newText;
                return;
            }
        }
        // If no text node found, prepend one
        element.insertBefore(document.createTextNode(newText), element.firstChild);
    }

    /**
     * Set a custom label (local update)
     */
    setCustomLabel(key, value) {
        if (value === null) {
            delete this.customLabels[key];
        } else {
            this.customLabels[key] = value;
        }
        
        // Update elements with this key
        document.querySelectorAll(`[data-key="${key}"]`).forEach(el => {
            const newValue = this.get(key);
            el.textContent = newValue;
        });
    }

    /**
     * Save a custom label to server
     */
    async saveCustomLabel(key, value) {
        const token = localStorage.getItem('token') || this.getCookie('access_token');
        
        try {
            const response = await fetch('/api/translations/label', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ key, value })
            });
            
            if (response.ok) {
                this.setCustomLabel(key, value);
                return true;
            }
        } catch (e) {
            console.error('Failed to save custom label:', e);
        }
        return false;
    }

    /**
     * Delete a custom label from server
     */
    async deleteCustomLabel(key) {
        const token = localStorage.getItem('token') || this.getCookie('access_token');
        
        try {
            const response = await fetch(`/api/translations/label/${encodeURIComponent(key)}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (response.ok) {
                this.setCustomLabel(key, null);
                return true;
            }
        } catch (e) {
            console.error('Failed to delete custom label:', e);
        }
        return false;
    }

    /**
     * Handle WebSocket translation update
     */
    handleTranslationUpdate(data) {
        if (data.type === 'translation_update') {
            this.setCustomLabel(data.key, data.value);
        } else if (data.type === 'language_change') {
            this.languageMode = data.language_mode;
            // Reload translations for new language
            this.init();
        } else if (data.type === 'translations_reset') {
            this.customLabels = {};
            this.updateAllLabels();
        }
    }

    /**
     * Set language mode on server
     */
    async setLanguageMode(mode) {
        const token = localStorage.getItem('token') || this.getCookie('access_token');
        
        try {
            const response = await fetch('/api/translations/language', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ language_mode: mode })
            });
            
            if (response.ok) {
                // Update will come via WebSocket broadcast
                return true;
            }
        } catch (e) {
            console.error('Failed to set language mode:', e);
        }
        return false;
    }

    /**
     * Get current language mode
     */
    getLanguageMode() {
        return this.languageMode;
    }
}

// Global instance
window.translationManager = new TranslationManager();

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Slight delay to ensure auth token is available
    setTimeout(() => {
        window.translationManager.init();
    }, 100);
});
