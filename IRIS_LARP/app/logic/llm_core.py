import os
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel
import google.generativeai as genai
from openai import OpenAI
from ..config import settings
from ..database import SessionLocal, SystemConfig

class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"

class LLMConfig(BaseModel):
    provider: LLMProvider = LLMProvider.OPENROUTER
    model_name: str = "google/gemini-2.0-flash-lite-preview-02-05:free"
    system_prompt: str = "You are a helpful assistant."

class LLMService:
    def __init__(self):
        # Clients are instantiated per request or lazily to handle key changes
        pass

    def _get_key(self, provider: LLMProvider) -> Optional[str]:
        db = SessionLocal()
        try:
            key_name = f"{provider.value.upper()}_API_KEY"
            # Prioritize DB
            config = db.query(SystemConfig).filter(SystemConfig.key == key_name).first()
            if config:
                return config.value
            # Fallback to Settings (Env)
            return getattr(settings, key_name, None)
        except Exception as e:
            print(f"Error fetching key for {provider}: {e}")
            return None
        finally:
            db.close()

    def list_models(self, provider: LLMProvider) -> List[str]:
        api_key = self._get_key(provider)
        if not api_key:
             # Return defaults if no key to allow UI to render something
             if provider == LLMProvider.OPENROUTER:
                 return ["google/gemini-2.0-flash-lite-preview-02-05:free", "mistralai/mistral-7b-instruct:free"]
             elif provider == LLMProvider.OPENAI:
                 return ["gpt-3.5-turbo", "gpt-4o"]
             elif provider == LLMProvider.GEMINI:
                 return ["gemini-pro", "gemini-1.5-flash"]
             return []

        try:
            if provider == LLMProvider.OPENAI:
                 client = OpenAI(api_key=api_key)
                 models = client.models.list()
                 return [m.id for m in models.data if "gpt" in m.id]

            elif provider == LLMProvider.GEMINI:
                genai.configure(api_key=api_key)
                models = genai.list_models()
                return [m.name for m in models if 'generateContent' in m.supported_generation_methods]

            elif provider == LLMProvider.OPENROUTER:
                # OpenRouter compatible with OpenAI Client
                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                )
                models = client.models.list()
                return [m.id for m in models.data]
                
        except Exception as e:
            print(f"Error listing models for {provider}: {e}")
            return []
        
        return []

    def generate_response(self, config: LLMConfig, history: List[Dict[str, str]]) -> str:
        api_key = self._get_key(config.provider)
        
        # MOCK FALLBACKS if no key
        if not api_key:
            return f"[MOCK {config.provider.name}] Evaluated input: {history[-1]['content'] if history else 'Empty'} using {config.model_name}"

        try:
            if config.provider == LLMProvider.OPENAI:
                return self._generate_openai(api_key, config, history)
            elif config.provider == LLMProvider.GEMINI:
                return self._generate_gemini(api_key, config, history)
            elif config.provider == LLMProvider.OPENROUTER:
                return self._generate_openrouter(api_key, config, history)
        except Exception as e:
            print(f"LLM Generation Error: {e}")
            return f"[SYSTEM ERROR: {str(e)}]"

    def _generate_openai(self, api_key: str, config: LLMConfig, history: List[Dict[str, str]]) -> str:
        client = OpenAI(api_key=api_key)
        messages = [{"role": "system", "content": config.system_prompt}]
        messages.extend(history)
        
        response = client.chat.completions.create(
            model=config.model_name,
            messages=messages
        )
        return response.choices[0].message.content

    def _generate_openrouter(self, api_key: str, config: LLMConfig, history: List[Dict[str, str]]) -> str:
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                default_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": settings.PROJECT_NAME,
                }
            )
            messages = [{"role": "system", "content": config.system_prompt}]
            messages.extend(history)
            
            response = client.chat.completions.create(
                model=config.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenRouter Error: {e}")
            # Fallback or re-raise
            raise e

    def _generate_gemini(self, api_key: str, config: LLMConfig, history: List[Dict[str, str]]) -> str:
        genai.configure(api_key=api_key)
        
        gemini_hist = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_hist.append({"role": role, "parts": [msg["content"]]})
            
        model = genai.GenerativeModel(config.model_name, system_instruction=config.system_prompt)
        chat = model.start_chat(history=gemini_hist[:-1] if len(gemini_hist) > 0 else [])
        
        last_msg = gemini_hist[-1]["parts"][0] if len(gemini_hist) > 0 else ""
        if not last_msg: return ""
        
        response = chat.send_message(last_msg)
        return response.text

llm_service = LLMService()
