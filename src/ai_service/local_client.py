import os
import time
import hashlib
import json
from typing import Optional, List, Dict

from pathlib import Path
from loguru import logger
from openai import OpenAI


class LocalDeepSeekClient:
    """Клиент для ИИ модели через OLLAMA сервис"""
    def __init__(
            self,
            base_url: Optional[str] = None,
            model_name: Optional[str] = None,
            cache_dir: str = "model/deepseek/cache",
            timeout: int = 300,
            max_retries: int = 3
    ):
        host = os.getenv("DEEPSEEK_HOST", "localhost")
        port = os.getenv("DEEPSEEK_PORT", "11434")
        self.base_url = base_url or f"http://{host}:{port}/v1"
        self.model_name = model_name or os.getenv("DEEPSEEK_MODEL_PATH", "deepseek-r1:7b"
                                                  )
        