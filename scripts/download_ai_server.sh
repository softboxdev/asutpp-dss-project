#!/bin/bash
# ============================================================
# СКРИПТ ЗАГРУЗКИ ЛОКАЛЬНЫХ МОДЕЛЕЙ DEEPSEEK
# ============================================================

set -e

# Цвета для вывода
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Загрузка локальных моделей DeepSeek${NC}"
echo -e "${GREEN}============================================${NC}"

# Проверка установки huggingface-cli
if ! command -v huggingface-cli &> /dev/null; then
    echo -e "${YELLOW}Установка huggingface-cli...${NC}"
    pip install -U "huggingface_hub[cli]"
fi

# Директория для моделей
MODELS_DIR="models/deepseek"
mkdir -p $MODELS_DIR

# Выбор модели через аргумент или по умолчанию
MODEL_SIZE=${1:-7b}

case $MODEL_SIZE in
    "1.5b")
        MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B"
        ;;
    "7b")
        MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"
        ;;
    "8b")
        MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Llama-8B"
        ;;
    "14b")
        MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B"
        ;;
    "32b")
        MODEL_NAME="deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
        ;;
    *)
        echo -e "${RED}Неизвестный размер: $MODEL_SIZE${NC}"
        echo "Доступные: 1.5b, 7b, 8b, 14b, 32b"
        exit 1
        ;;
esac

echo -e "${YELLOW}Загрузка модели: $MODEL_NAME${NC}"
echo -e "${YELLOW}Директория: $MODELS_DIR${NC}"

# Загрузка
huggingface-cli download $MODEL_NAME \
    --local-dir $MODELS_DIR/$(basename $MODEL_NAME) \
    --local-dir-use-symlinks False

echo -e "${GREEN}✅ Модель загружена: $MODELS_DIR/$(basename $MODEL_NAME)${NC}"

# Проверка размера
du -sh $MODELS_DIR/$(basename $MODEL_NAME)

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Загрузка завершена!${NC}"
echo -e "${GREEN}============================================${NC}"