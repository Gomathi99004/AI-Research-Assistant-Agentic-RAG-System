import asyncio
from typing import Optional
from app.core.config import settings
from app.core.exceptions import LLMUnavailableError

try:
    from groq import AsyncGroq
    import google.generativeai as genai
except ImportError:
    pass

class LLMManager:
    def __init__(self):
        self.groq_keys = settings.groq_keys
        self.gemini_keys = settings.gemini_keys
        self.current_groq_idx = 0
        self.current_gemini_idx = 0

    def _get_groq_client(self):
        if not self.groq_keys:
            return None
        key = self.groq_keys[self.current_groq_idx]
        return AsyncGroq(api_key=key)

    def _rotate_groq(self):
        if self.groq_keys:
            self.current_groq_idx = (self.current_groq_idx + 1) % len(self.groq_keys)
    
    def _rotate_gemini(self):
        if self.gemini_keys:
            self.current_gemini_idx = (self.current_gemini_idx + 1) % len(self.gemini_keys)

    def _get_gemini_key(self):
        if not self.gemini_keys:
            return None
        return self.gemini_keys[self.current_gemini_idx]

    async def call_llm(self, prompt: str, max_tokens: int = 1024) -> str:
        # Try Groq keys first
        attempts = 0
        while attempts < len(self.groq_keys):
            client = self._get_groq_client()
            if not client:
                break
            try:
                chat_completion = await client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=settings.GROQ_MODEL,
                    max_tokens=max_tokens,
                )
                return chat_completion.choices[0].message.content
            except Exception as e:
                print(f"[LLM Debug] Groq failed on key #{self.current_groq_idx}: {e}")
                self._rotate_groq()
                attempts += 1
                await asyncio.sleep(1)

        # If Groq failed, fallback to Gemini
        attempts = 0
        while attempts < len(self.gemini_keys):
            key = self._get_gemini_key()
            if not key:
                break
            try:
                genai.configure(api_key=key)
                model = genai.GenerativeModel(settings.GEMINI_MODEL)
                response = model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"[LLM Debug] Gemini failed on key #{self.current_gemini_idx}: {e}")
                self._rotate_gemini()
                attempts += 1
                await asyncio.sleep(1)

        raise LLMUnavailableError("All Groq and Gemini API keys exhausted or failed.")

llm_manager = LLMManager()

async def call_llm(prompt: str, max_tokens: int = 1024) -> str:
    return await llm_manager.call_llm(prompt, max_tokens)
