"""Клиент для AI Service (Ollama)."""
import os
import time
import hashlib
import json
from typing import Optional, List, Dict
from pathlib import Path
from loguru import logger
from openai import OpenAI


class AIClient:
    """Клиент для локального AI сервера (Ollama)."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        cache_dir: Optional[str] = None,
        timeout: int = 300,
        max_retries: int = 3,
    ):
        host = os.getenv("AI_HOST", "localhost")
        port = os.getenv("AI_PORT", "11434")
        
        self.base_url = base_url or f"http://{host}:{port}/v1"
        self.model_name = model_name or os.getenv("AI_MODEL", "deepseek-r1:7b")
        self.timeout = timeout
        self.max_retries = max_retries
        
        self.client = OpenAI(
            base_url=self.base_url,
            api_key="ollama",
            timeout=timeout,
        )
        
        self.cache_dir = Path(cache_dir or os.getenv(
            "AI_CACHE_DIR", "models/ai_server/cache"
        ))
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self._check_connection()
        logger.info(f"AIClient готов: {self.base_url}")
    
    def _check_connection(self):
        try:
            models = self.client.models.list()
            model_ids = [m.id for m in models.data]
            logger.info(f"Доступные модели: {model_ids}")
            if self.model_name not in model_ids:
                logger.warning(
                    f"Модель '{self.model_name}' не найдена. "
                    f"Загрузите: ollama pull {self.model_name}"
                )
        except Exception as e:
            raise ConnectionError(
                f"AI Service недоступен по {self.base_url}. "
                f"Запустите: ollama serve"
            ) from e
    
    def _cache_key(self, prompt: str, params: Dict) -> str:
        content = prompt + json.dumps(params, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        use_cache: bool = True,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        params = {"temperature": temperature, "max_tokens": max_tokens}
        key = self._cache_key(prompt + (system_prompt or ""), params)
        
        # Кэш
        if use_cache:
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)['response']
        
        # Запрос
        for attempt in range(self.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                result = response.choices[0].message.content
                
                if use_cache:
                    cache_file = self.cache_dir / f"{key}.json"
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump({'response': result}, f, ensure_ascii=False)
                
                return result
            except Exception as e:
                logger.warning(f"Попытка {attempt + 1}/{self.max_retries}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise


_client: Optional[AIClient] = None


def get_ai_client() -> AIClient:
    global _client
    if _client is None:
        _client = AIClient()
    return _client
