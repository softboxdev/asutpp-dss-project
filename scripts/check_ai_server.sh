#!/bin/bash
echo "Проверка ИИ сервера..."

if curl -s http://localhost:11434/v1/models > /dev/null 2>&1; then
    echo "Проверка пройдена, ИИ модель работает"
    curl -s http://localhost:11434/v1/models | jq '.data[].id'
else
    echo "ИИ сервер недоступен"
    echo "Запустите сервер ИИ: ./scripts/start_ai_server.sh"
    exit 1
fi
