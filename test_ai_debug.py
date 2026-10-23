"""Полная диагностика AI в DACIE."""
from pathlib import Path
from loguru import logger
import sys

logger.remove()
logger.add(sys.stdout, level="DEBUG", 
           format="{time:HH:mm:ss} | {level} | {message}")

# 1. Проверка AI-клиента
from src.ai_service.local_client import get_ai_client
client = get_ai_client()
print(f"\n✅ AIClient: {client.base_url}")
print(f"   Модель: {client.model_name}")

# 2. Тест прямого вызова
from src.ai_service.prompts.entity_extraction import (
    ENTITY_EXTRACTION_SYSTEM, build_entity_extraction_prompt,
)

test_text = "Система должна контролировать температуру 150-200°C. SIL 2."
response = client.generate(
    prompt=build_entity_extraction_prompt(test_text),
    system_prompt=ENTITY_EXTRACTION_SYSTEM,
    temperature=0.1, max_tokens=1024, use_cache=False,
)
print(f"\n✅ Прямой вызов: ответ {len(response)} символов")
print(f"   {response[:200]}")

# 3. Проверка DACIE
from src.ml.dacie.entity_extractor import DACIE

dacie = DACIE(use_ai=True)
print(f"\n✅ DACIE: use_ai={dacie.use_ai}")

# 4. Тест на коротком тексте
result = dacie.process(test_text)
print(f"\n✅ Короткий текст: {len(result['entities'])} сущностей")

# 5. Тест на полном ТЗ
tz_path = Path("data/test_examples/chemical_reactor_tz.txt")
if tz_path.exists():
    full_tz = tz_path.read_text(encoding='utf-8')
    result = dacie.process(full_tz)
    print(f"\n✅ Полное ТЗ: {len(result['entities'])} сущностей")
    
    for e in result['entities'][:5]:
        print(f"   [{e.get('source')}] {e.get('type')}: {e.get('text')[:40]}")
