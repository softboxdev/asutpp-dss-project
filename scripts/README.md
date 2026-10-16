# Остановить все процессы
```bash
# Убедитесь, что DeepSeek остановлен
make stop-deepseek 2>/dev/null || pkill -f vllm

# Выйдите из виртуального окружения
exit
```


# Сборка и  Подготовка среды

```bash
# Очистите lock-файл
rm poetry.lock
# Удалите старое виртуальное окружение Poetry
poetry env remove --all
# Посмотреть список окружений
poetry env list
# Удалить все окружения проекта
poetry env use python3.12
poetry install

# 6. Проверить
poetry shell
python --version
python -c "import numpy, spacy, torch; print('OK')"

# 7. Продолжить работу
make start-deepseek-bg
make check-deepseek
```

# Использование Ollama

```bash
# Установите Ollama
curl -fsSL https://ollama.com/install.sh | sh
# Загрузите DeepSeek
ollama pull deepseek-r1:7b
ollama pull deepseek-r1:1.5b
# Проверить список моделей
ollama list
# Ollama автоматически запускает сервер на порту 11434
ollama serve
# Узнать статус
ollama --version

# Запустить как сервис (в фоне)
sudo systemctl enable ollama
sudo systemctl start ollama

# Или вручную
ollama serve &

# Проверить статус
sudo systemctl status ollama
```
# Тестовый запрос через curl
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



.env:
```
cat > .env << 'EOF'
# ============================================================
# КОНФИГУРАЦИЯ ПОЛНОСТЬЮ ЛОКАЛЬНОГО ПРОЕКТА
# ============================================================

# DeepSeek (локальный)
DEEPSEEK_MODEL_PATH=models/deepseek/DeepSeek-R1-Distill-Qwen-7B
DEEPSEEK_HOST=localhost
DEEPSEEK_PORT=8001
DEEPSEEK_MAX_TOKENS=2048
DEEPSEEK_TEMPERATURE=0.1
DEEPSEEK_GPU_MEMORY_UTILIZATION=0.9
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
DSAL_ACTIVE_LEARNING_INTERVAL=10

# UI
STREAMLIT_PORT=8501
API_PORT=8000
EOF
```


