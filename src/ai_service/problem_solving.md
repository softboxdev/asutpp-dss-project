# Решение конфликта: vLLM vs numpy vs torch

## Анализ проблемы

```
vLLM 0.6.3-0.6.6 требует:
  - torch == 2.4.0 (фиксированная версия)
  - numpy < 2.0.0

А вы хотите:
  - torch ^2.5.0 (>=2.5.0)
  - numpy >=2.0.0,<2.1.0

Конфликт неустраним на уровне pyproject.toml
```

**Причина:** vLLM жёстко фиксирует `torch 2.4.0` и `numpy <2.0.0` — это архитектурное ограничение старых версий.

**Решения:**
1. **Использовать более новую версию vLLM** (0.7.x+, где нет фиксации torch)
2. **Использовать Ollama вместо vLLM** (рекомендуется — самый простой путь)
3. **Понизить torch и numpy** (не рекомендуется, сломает другие зависимости)

---

## ✅ РЕКОМЕНДУЕМОЕ РЕШЕНИЕ: Ollama вместо vLLM

**Ollama** — это отдельный сервис (не Python-пакет), работает через OpenAI-совместимый API. Никаких конфликтов зависимостей.

### Преимущества Ollama

| Критерий | vLLM | Ollama |
|----------|------|--------|
| Конфликты зависимостей | ❌ Много | ✅ Нет |
| Установка | Сложная | `curl ... \| sh` |
| Работа с Python | Через пакет | Через HTTP API |
| Производительность | Высокая | Высокая |
| Поддержка GPU | ✅ | ✅ |
| Простота | Сложная | Очень простая |

### Шаг 1. Установите Ollama

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Проверка:**
```bash
ollama --version
```

### Шаг 2. Запустите сервер Ollama

```bash
# Запустить как сервис (в фоне)
sudo systemctl enable ollama
sudo systemctl start ollama

# Или вручную
ollama serve &

# Проверить статус
sudo systemctl status ollama
```

### Шаг 3. Загрузите модель DeepSeek

```bash
# Модель 7B (рекомендуется, ~5 GB)
ollama pull deepseek-r1:7b

# Или меньше — для тестов
ollama pull deepseek-r1:1.5b

# Проверить список моделей
ollama list
```

**Что вы увидите:**
```
NAME                ID              SIZE      MODIFIED
deepseek-r1:7b      xxx             4.7 GB    2 minutes ago
```

### Шаг 4. Проверьте работу Ollama

```bash
# Тестовый запрос через curl
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-r1:7b",
    "messages": [{"role": "user", "content": "Привет!"}],
    "max_tokens": 50
  }'
```

**Ожидаемый ответ:**
```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "deepseek-r1:7b",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "Привет! Чем могу помочь?"
    },
    "finish_reason": "stop"
  }]
}
```

---

## Исправленный `pyproject.toml` (без vLLM)

**Замените полностью:**

```bash
cat > pyproject.toml << 'EOF'
[tool.poetry]
name = "asutp-dss-local"
version = "0.1.0"
description = "Локальная СППР для проектирования архитектуры ПО АСУ ТП"
authors = ["Ваше Имя <email@example.com>"]
packages = [{include = "src"}]

[tool.poetry.dependencies]
python = ">=3.12,<3.13"

# === DeepSeek через Ollama (без vLLM!) ===
openai = "^1.50.0"
huggingface-hub = "^0.26.0"

# === Ядро ML ===
torch = {version = "^2.5.0", source = "pytorch"}
torch-geometric = "^2.6.0"
transformers = "^4.46.0"
sentence-transformers = "^3.3.0"
accelerate = "^1.1.0"
bitsandbytes = "^0.44.0"

# === Классический ML ===
xgboost = "^2.1.0"
lightgbm = "^4.5.0"
scikit-learn = "^1.5.0"

# === Оптимизация ===
pymoo = "^0.6.1"
simpy = "^4.1.1"

# === XAI ===
shap = "^0.46.0"

# === NLP ===
spacy = "^3.8.0"
nltk = "^3.9.0"

# === Парсинг документов ===
pypdf2 = "^3.0.1"
python-docx = "^1.1.0"

# === API + UI ===
fastapi = "^0.115.0"
uvicorn = {extras = ["standard"], version = "^0.32.0"}
pydantic = "^2.10.0"
pydantic-settings = "^2.6.0"
streamlit = "^1.40.0"
typer = "^0.13.0"
rich = "^13.9.0"

# === Хранилище ===
sqlalchemy = "^2.0.36"
networkx = "^3.4.0"

# === Утилиты ===
pyyaml = "^6.0.2"
python-dotenv = "^1.0.1"
loguru = "^0.7.2"
tqdm = "^4.67.0"
joblib = "^1.4.2"
numpy = ">=2.0.0,<2.1.0"
pandas = "^2.2.3"
scipy = "^1.14.0"

[tool.poetry.group.dev.dependencies]
pytest = "^8.3.0"
pytest-cov = "^6.0.0"
pytest-asyncio = "^0.24.0"
jupyter = "^1.1.0"
ipykernel = "^6.29.0"
ruff = "^0.8.0"
black = "^24.10.0"
isort = "^5.13.2"
mypy = "^1.13.0"
pre-commit = "^4.0.0"

[[tool.poetry.source]]
name = "pytorch"
url = "https://download.pytorch.org/whl/cu121"
priority = "explicit"

[build-system]
requires = ["poetry-core>=2.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.ruff]
line-length = 100
target-version = "py312"
select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM"]
ignore = ["E501", "B008"]

[tool.black]
line-length = 100
target-version = ['py312']

[tool.isort]
profile = "black"
line_length = 100

[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=src --cov-report=html --cov-report=term"
asyncio_mode = "auto"
EOF
```

**Ключевое изменение:** убрана строка `vllm = "^0.6.3"`.

---

## Пошаговая переустановка

```bash
cd ~/projects/asutp-dss-local

# 1. Удалить старые зависимости и lock
poetry env remove --all
rm -f poetry.lock

# 2. Убедиться, что Python 3.12
python3.12 --version

# 3. Указать Poetry использовать Python 3.12
poetry env use python3.12

# 4. Установить зависимости
poetry install
```

**Ожидаемый результат:**
```
Creating virtualenv asutp-dss-local-xxxxx-py3.12
Updating dependencies
Resolving dependencies... (60-90s)
Writing lock file
Installing dependencies...
Installing the current project: asutp-dss-local (0.1.0)
```

---

## Обновите `.env` для Ollama

```bash
cat > .env << 'EOF'
# ============================================================
# Конфигурация для Ollama (вместо vLLM)
# ============================================================

# DeepSeek через Ollama
DEEPSEEK_HOST=localhost
DEEPSEEK_PORT=11434
DEEPSEEK_MODEL_PATH=deepseek-r1:7b
DEEPSEEK_MAX_TOKENS=2048
DEEPSEEK_TEMPERATURE=0.1
DEEPSEEK_CACHE_DIR=models/deepseek/cache
DEEPSEEK_CONFIDENCE_THRESHOLD=0.85

# Общие настройки
APP_NAME=ASUTP-DSS-Local
APP_ENV=development
DEBUG=true
LOG_LEVEL=INFO

# Хранилище
SQLITE_PATH=data/asutp.db
DOCUMENTS_DIR=data/raw
MODELS_DIR=models
CACHE_DIR=data/cache

# ML
ML_DEVICE=cuda
ML_BATCH_SIZE=32
ML_NUM_WORKERS=4

# DSAL
DSAL_ENABLED=true
DSAL_SYNTHETIC_RATIO=0.3

# UI
STREAMLIT_PORT=8501
API_PORT=8000
EOF
```

---

## Обновите `src/deepseek/local_client.py`

Замените содержимое файла:

```bash
cat > src/deepseek/local_client.py << 'PYEOF'
"""
Клиент для локальной DeepSeek через Ollama.
Ollama предоставляет OpenAI-совместимый API на порту 11434.
"""
import os
import time
import hashlib
import json
from typing import Optional, List, Dict
from pathlib import Path
from loguru import logger
from openai import OpenAI

class LocalAIClient:
    """Клиент для DeepSeek через Ollama."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        model_name: Optional[str] = None,
        cache_dir: str = "models/deepseek/cache",
        timeout: int = 300,
        max_retries: int = 3
    ):
        # Читаем из .env или используем значения по умолчанию
        host = os.getenv("DEEPSEEK_HOST", "localhost")
        port = os.getenv("DEEPSEEK_PORT", "11434")
        
        self.base_url = base_url or f"http://{host}:{port}/v1"
        self.model_name = model_name or os.getenv(
            "DEEPSEEK_MODEL_PATH", "deepseek-r1:7b"
        )
        
        self.timeout = timeout
        self.max_retries = max_retries
        
        # OpenAI-совместимый клиент
        self.client = OpenAI(
            base_url=self.base_url,
            api_key="ollama",  # Ollama не проверяет, но требуется
            timeout=timeout,
        )
        
        # Кэш
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Проверка подключения
        self._check_connection()
        logger.info(f"LocalAIClient готов: {self.base_url}")
    
    def _check_connection(self):
        """Проверка доступности Ollama."""
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
            logger.error(f"Ollama недоступен: {e}")
            raise ConnectionError(
                f"Ollama недоступен по адресу {self.base_url}. "
                f"Запустите: ollama serve"
            )
    
    def _get_cache_key(self, prompt: str, params: Dict) -> str:
        content = prompt + json.dumps(params, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[str]:
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)['response']
            except Exception as e:
                logger.warning(f"Ошибка чтения кэша: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, prompt: str, response: str):
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'prompt': prompt,
                    'response': response,
                    'timestamp': time.time(),
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning(f"Ошибка сохранения кэша: {e}")
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        use_cache: bool = True,
    ) -> str:
        """Генерация ответа через Ollama."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        params = {"temperature": temperature, "max_tokens": max_tokens}
        cache_key = self._get_cache_key(prompt + (system_prompt or ""), params)
        
        # Проверка кэша
        if use_cache:
            cached = self._load_from_cache(cache_key)
            if cached is not None:
                logger.debug(f"Кэш hit: {cache_key[:8]}")
                return cached
        
        # Запрос с retry
        last_error = None
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
                    self._save_to_cache(cache_key, prompt, result)
                
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"Попытка {attempt + 1}/{self.max_retries}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise RuntimeError(
                        f"Не удалось получить ответ: {last_error}"
                    )
    
    def generate_batch(
        self,
        prompts: List[str],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """Батчевая генерация."""
        results = []
        for i, prompt in enumerate(prompts):
            logger.info(f"Обработка {i + 1}/{len(prompts)}")
            result = self.generate(prompt, system_prompt, **kwargs)
            results.append(result)
        return results


_client: Optional[LocalAIClient] = None


def get_ai_client() -> LocalAIClient:
    """Singleton клиент."""
    global _client
    if _client is None:
        _client = LocalAIClient()
    return _client
PYEOF
```

---

## Обновите `scripts/start_deepseek_server.sh` для Ollama

```bash
cat > scripts/start_deepseek_server.sh << 'EOF'
#!/bin/bash
# ============================================================
# Запуск Ollama сервера с DeepSeek
# ============================================================

set -e

MODEL_NAME=${MODEL_NAME:-"deepseek-r1:7b"}

echo "============================================"
echo "Запуск Ollama сервера DeepSeek"
echo "============================================"
echo "Модель: $MODEL_NAME"
echo "Порт: 11434"
echo "============================================"

# Проверка установки Ollama
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama не установлен"
    echo "Установите: curl -fsSL https://ollama.com/install.sh | sh"
    exit 1
fi

# Проверка статуса сервиса
if systemctl is-active --quiet ollama; then
    echo "✅ Ollama сервис уже запущен"
else
    echo "Запуск Ollama сервиса..."
    sudo systemctl start ollama
    sleep 2
fi

# Проверка наличия модели
if ! ollama list | grep -q "$MODEL_NAME"; then
    echo "Загрузка модели $MODEL_NAME..."
    ollama pull $MODEL_NAME
fi

# Проверка
echo ""
echo "Проверка API..."
if curl -s http://localhost:11434/v1/models > /dev/null; then
    echo "✅ Ollama API доступен на http://localhost:11434"
    curl -s http://localhost:11434/v1/models | jq '.data[].id'
else
    echo "❌ API недоступен"
    exit 1
fi

echo ""
echo "============================================"
echo "Готово! Ollama работает в фоне как сервис"
echo "Логи: sudo journalctl -u ollama -f"
echo "============================================"
EOF

chmod +x scripts/start_deepseek_server.sh
```

---

## Обновите `scripts/check_deepseek.sh`

```bash
cat > scripts/check_deepseek.sh << 'EOF'
#!/bin/bash

echo "Проверка Ollama сервера..."

if curl -s http://localhost:11434/v1/models > /dev/null 2>&1; then
    echo "✅ Ollama работает"
    echo "Доступные модели:"
    curl -s http://localhost:11434/v1/models | jq -r '.data[].id'
else
    echo "❌ Ollama недоступен"
    echo "Запустите: sudo systemctl start ollama"
    exit 1
fi
EOF

chmod +x scripts/check_deepseek.sh
```

---

## Обновите `Makefile`

```bash
cat > Makefile << 'EOF'
.PHONY: help install start-deepseek stop-deepseek check-deepseek test-deepseek run-cli run-ui clean gpu-info

GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RED    := $(shell tput -Txterm setaf 1)
RESET  := $(shell tput -Txterm sgr0)

help:
	@echo "${GREEN}Доступные команды:${RESET}"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  ${YELLOW}%-25s${RESET} %s\n", $$1, $$2}'

install: ## Установить зависимости
	poetry install

start-deepseek: ## Запустить Ollama сервер
	./scripts/start_deepseek_server.sh

start-deepseek-bg: ## Проверить/запустить Ollama
	sudo systemctl start ollama 2>/dev/null || ollama serve &
	@sleep 2
	@echo "Ollama запущен"

stop-deepseek: ## Остановить Ollama
	@sudo systemctl stop ollama 2>/dev/null || pkill -f "ollama serve" || true
	@echo "Ollama остановлен"

check-deepseek: ## Проверить Ollama
	./scripts/check_deepseek.sh

test-deepseek: ## Тестовый запрос
	@curl -s -X POST http://localhost:11434/v1/chat/completions \
		-H "Content-Type: application/json" \
		-d '{"model":"deepseek-r1:7b","messages":[{"role":"user","content":"Скажи привет одним словом"}],"max_tokens":20}' \
		| jq -r '.choices[0].message.content'

pull-model: ## Загрузить модель DeepSeek
	ollama pull deepseek-r1:7b

pull-model-small: ## Загрузить меньшую модель
	ollama pull deepseek-r1:1.5b

run-cli: ## Запустить CLI
	poetry run python -m src.main analyze

run-ui: ## Запустить Streamlit UI
	poetry run streamlit run src/ui/streamlit_app.py

check: ## Проверка системы
	poetry run python -m src.main check

test: ## Запуск тестов
	poetry run pytest tests/ -v

clean: ## Очистка
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf htmlcov/ .coverage .pytest_cache

gpu-info: ## Информация о GPU
	@nvidia-smi
EOF
```

---

## Финальная последовательность команд

```bash
# ========== 1. Установить Ollama (один раз) ==========
curl -fsSL https://ollama.com/install.sh | sh

# ========== 2. Запустить сервис ==========
sudo systemctl enable ollama
sudo systemctl start ollama

# ========== 3. Загрузить DeepSeek (один раз, 3-5 мин) ==========
ollama pull deepseek-r1:7b

# ========== 4. Перейти в проект и очистить Poetry ==========
cd ~/projects/asutp-dss-local
poetry env remove --all
rm -f poetry.lock

# ========== 5. Заменить pyproject.toml (без vllm!) ==========
# (скопировать содержимое выше)

# ========== 6. Указать Python 3.12 и установить ==========
poetry env use python3.12
poetry install

# ========== 7. Проверить ==========
make check-deepseek
make test-deepseek

# ========== 8. Запустить анализ ==========
poetry shell
python -m src.main check
python -m src.main analyze
```

---

## Ожидаемый результат `poetry install`

```
Creating virtualenv asutp-dss-local-xxxxx-py3.12 in /home/user/.cache/pypoetry/virtualenvs
Updating dependencies
Resolving dependencies... (45.2s)

Package operations: 87 installs, 0 updates, 0 removals

  • Installing numpy (2.0.2)
  • Installing torch (2.5.1+cu121)
  • Installing transformers (4.46.3)
  • Installing spacy (3.8.x)
  • Installing xgboost (2.1.3)
  • Installing shap (0.46.0)
  • Installing openai (1.50.0)
  ...

Installing the current project: asutp-dss-local (0.1.0)
```

**✅ Никаких конфликтов, потому что vLLM убран.**

---

## Сравнение: vLLM vs Ollama для вашего проекта

| Критерий | vLLM | **Ollama** |
|----------|------|------------|
| Установка | Сложная (конфликты) | Простая (1 команда) |
| Работа с Python 3.12 | ❌ Конфликты | ✅ Работает |
| torch версия | Требует 2.4.0 | Не важно |
| numpy версия | Требует <2.0.0 | Не важно |
| API | OpenAI-совместимый | OpenAI-совместимый |
| Производительность | Максимальная | Высокая |
| Управление моделями | Вручную | `ollama pull` |
| **Рекомендация** | Production с кластером | **✅ MVP и диссертация** |

---

## Что делать, если хочется именно vLLM

Если для диссертации критично использовать **vLLM** (например, для production-развёртывания), то придётся понизить версии:

```toml
# Компромиссная конфигурация с vLLM
python = ">=3.11,<3.12"  # vLLM лучше работает на 3.11

# vLLM
vllm = "^0.6.3"

# Совместимые версии
torch = {version = "==2.4.0", source = "pytorch"}  # ← фиксируем 2.4.0
numpy = ">=1.26.0,<2.0.0"                          # ← понижаем до 1.x

# И все остальные пакеты должны быть совместимы с numpy <2.0.0
```

**Но это создаст новые конфликты с pandas 2.2.x, transformers 4.46 и другими.** Поэтому **Ollama — правильный выбор для MVP и диссертации**.

---

## Итог

1. ✅ **Используйте Ollama** вместо vLLM
2. ✅ **Уберите `vllm` из `pyproject.toml`**
3. ✅ **Оставьте `openai`** (работает с Ollama через OpenAI-совместимый API)
4. ✅ **Исправьте `.env`** — порт 11434
5. ✅ **Замените `local_client.py`** — добавьте поддержку Ollama
6. ✅ **Переустановите Poetry** — `poetry install` пройдёт без ошибок

**После этих шагов `poetry install` пройдёт успешно.** Запустите команды и напишите результат — если что-то ещё не так, помогу разобраться.
