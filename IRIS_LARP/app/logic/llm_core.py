import os
from enum import Enum
from typing import List, Dict, Optional
from pydantic import BaseModel
import google.generativeai as genai
from openai import AsyncOpenAI
from ..config import settings
from ..database import SessionLocal, SystemConfig

class LLMProvider(str, Enum):
    OPENAI = "openai"
    GEMINI = "gemini"
    OPENROUTER = "openrouter"

class LLMConfig(BaseModel):
    provider: LLMProvider = LLMProvider.OPENROUTER
    model_name: str = "google/gemini-2.5-flash-lite"
    system_prompt: str = "You are a helpful assistant."



class LLMService:
    def __init__(self):
        # Clients are instantiated per request or lazily to handle key changes
        pass

    def _get_key(self, provider: LLMProvider) -> Optional[str]:
        # STRICT SECURITY: Keys are loaded ONLY from environment variables (.env)
        # We do not load from DB to prevent persistence in potentially unencrypted storage.
        key_name = f"{provider.value.upper()}_API_KEY"
        return getattr(settings, key_name, None)

    async def list_models(self, provider: LLMProvider) -> List[str]:
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
                 client = AsyncOpenAI(api_key=api_key)
                 models = await client.models.list()
                 return [m.id for m in models.data if "gpt" in m.id]

            elif provider == LLMProvider.GEMINI:
                genai.configure(api_key=api_key)
                models = genai.list_models()
                return [m.name for m in models if 'generateContent' in m.supported_generation_methods]

            elif provider == LLMProvider.OPENROUTER:
                # OpenRouter compatible with OpenAI Client
                client = AsyncOpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                )
                models = await client.models.list()
                return [m.id for m in models.data]
                
        except Exception as e:
            print(f"Error listing models for {provider}: {e}")
            return []
        
        return []

    async def generate_response(self, config: LLMConfig, history: List[Dict[str, str]]) -> str:
        api_key = self._get_key(config.provider)
        
        # MOCK FALLBACKS if no key
        if not api_key:
            return f"[MOCK {config.provider.name}] Evaluated input: {history[-1]['content'] if history else 'Empty'} using {config.model_name}"

        try:
            if config.provider == LLMProvider.OPENAI:
                return await self._generate_openai(api_key, config, history)
            elif config.provider == LLMProvider.GEMINI:
                return await self._generate_gemini(api_key, config, history)
            elif config.provider == LLMProvider.OPENROUTER:
                return await self._generate_openrouter(api_key, config, history)
        except Exception as e:
            print(f"LLM Generation Error: {e}")
            return f"[SYSTEM ERROR: {str(e)}]"

    async def evaluate_submission(self, prompt: str, submission: str, config: Optional[LLMConfig] = None) -> int:
        full_user_prompt = f"TASK PROMPT: {prompt}\nUSER SUBMISSION: {submission}\n\nRate the submission from 0 to 100 based on creativity and relevance. Return ONLY the number."
        
        try:
            # Use provided config or auto-detect
            effective_config = config
            if not effective_config:
                # Dynamically select provider
                if self._get_key(LLMProvider.OPENROUTER):
                    effective_config = LLMConfig(provider=LLMProvider.OPENROUTER, model_name="google/gemini-2.5-flash-lite")
                elif self._get_key(LLMProvider.GEMINI):
                    effective_config = LLMConfig(provider=LLMProvider.GEMINI, model_name="gemini-1.5-flash")
                elif self._get_key(LLMProvider.OPENAI):
                    effective_config = LLMConfig(provider=LLMProvider.OPENAI, model_name="gpt-4o-mini")
                else:
                    return 50 # No provider available

            resp = await self.generate_response(effective_config, [{"role": "user", "content": full_user_prompt}])
            clean_resp = ''.join(filter(str.isdigit, resp))
            return int(clean_resp) if clean_resp else 50
        except Exception:
            return 50

    async def rewrite_message(self, content: str, instruction: str, config: Optional[LLMConfig] = None) -> str:
        """
        Rewrites the agent's message based on the instruction (Optimizer).
        Allows passing a custom LLMConfig so ROOT can pick provider/model per role.
        """
        prompt_content = (
            f"Original message: '{content}'\n\n"
            f"Instruction: {instruction}\n\n"
            "Rewrite the message to match the instruction. Return ONLY the rewritten text, nothing else."
        )

        effective_config = config or LLMConfig(
            provider=LLMProvider.OPENROUTER,
            model_name="google/gemini-2.5-flash-lite",
            system_prompt="You are a text rewriter. You strictly follow instructions."
        )
        
        history = [{"role": "user", "content": prompt_content}]

        return await self.generate_response(effective_config, history)

    async def generate_task_description(self, user_profile: dict, config: Optional[LLMConfig] = None) -> str:
        """
        Generate a task description based on user profile.
        user_profile should contain: username, status_level, credits
        """
        username = user_profile.get("username", "unknown")
        status = user_profile.get("status_level", "low")
        credits = user_profile.get("credits", 0)
        
        prompt_content = (
            f"Vygeneruj krátký pracovní úkol pro uživatele v korporátním systému IRIS.\n\n"
            f"Profil uživatele:\n"
            f"- Jméno: {username}\n"
            f"- Status: {status}\n"
            f"- Kredity: {credits}\n\n"
            f"Pravidla:\n"
            f"- Úkol musí být splnitelný textovou odpovědí (popis, návrh, analýza)\n"
            f"- Pro status 'low': jednoduché úkoly (přepis, shrnutí)\n"
            f"- Pro status 'mid': střední obtížnost (analýza, návrh)\n"
            f"- Pro status 'high': komplexní úkoly (strategie, rozhodnutí)\n"
            f"- Pro status 'party': kreativní/zábavné úkoly\n\n"
            f"Odpověz POUZE textem úkolu v češtině, bez úvodu nebo vysvětlení. Max 2-3 věty."
        )

        effective_config = config or LLMConfig(
            provider=LLMProvider.OPENROUTER,
            model_name="google/gemini-2.5-flash-lite",
            system_prompt="Jsi asistent pro generování pracovních úkolů v korporátním prostředí."
        )

        history = [{"role": "user", "content": prompt_content}]
        
        try:
            result = await self.generate_response(effective_config, history)
            return result.strip() if result else "Proveďte analýzu aktuálního stavu systému a navrhněte zlepšení."
        except Exception as e:
            print(f"Task generation error: {e}")
            return "Proveďte analýzu aktuálního stavu systému a navrhněte zlepšení."

    async def _generate_openai(self, api_key: str, config: LLMConfig, history: List[Dict[str, str]]) -> str:
        client = AsyncOpenAI(api_key=api_key)
        messages = [{"role": "system", "content": config.system_prompt}]
        messages.extend(history)
        
        response = await client.chat.completions.create(
            model=config.model_name,
            messages=messages
        )
        return response.choices[0].message.content

    async def _generate_openrouter(self, api_key: str, config: LLMConfig, history: List[Dict[str, str]]) -> str:
        try:
            client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                default_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": settings.PROJECT_NAME,
                }
            )
            messages = [{"role": "system", "content": config.system_prompt}]
            messages.extend(history)
            
            response = await client.chat.completions.create(
                model=config.model_name,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenRouter Error: {e}")
            # Fallback or re-raise
            raise e

    async def _generate_gemini(self, api_key: str, config: LLMConfig, history: List[Dict[str, str]]) -> str:
        genai.configure(api_key=api_key)
        
        gemini_hist = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_hist.append({"role": role, "parts": [msg["content"]]})
            
        model = genai.GenerativeModel(config.model_name, system_instruction=config.system_prompt)
        chat = model.start_chat(history=gemini_hist[:-1] if len(gemini_hist) > 0 else [])
        
        last_msg = gemini_hist[-1]["parts"][0] if len(gemini_hist) > 0 else ""
        if not last_msg: return ""
        
        response = await chat.send_message_async(last_msg)
        return response.text

llm_service = LLMService()
