.PHONY: help install download-model start-deepseek stop-deepseek check-deepseek test run-cli run-ui clean

GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

help:
	@echo "${GREEN}Доступные команды:${RESET}"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  ${YELLOW}%-25s${RESET} %s\n", $$1, $$2}'

install: ## Установить зависимости
	poetry install

download-model: ## Загрузить модель DeepSeek 7B
	huggingface-cli download deepseek-ai/DeepSeek-R1-Distill-Qwen-7B \
		--local-dir models/deepseek/DeepSeek-R1-Distill-Qwen-7B \
		--local-dir-use-symlinks False

start-deepseek: ## Запустить DeepSeek сервер
	./scripts/start_deepseek_server.sh

start-deepseek-bg: ## Запустить DeepSeek в фоне
	@mkdir -p logs
	nohup ./scripts/start_deepseek_server.sh > logs/deepseek_server.log 2>&1 &
	@echo "DeepSeek запущен, PID: $$!"
	@echo "Логи: logs/deepseek_server.log"

stop-deepseek: ## Остановить DeepSeek
	@pkill -f "vllm.entrypoints.openai.api_server" || true
	@echo "DeepSeek остановлен"

check-deepseek: ## Проверить DeepSeek
	./scripts/check_deepseek.sh

test-deepseek: ## Тестовый запрос к DeepSeek
	curl -s -X POST http://localhost:8001/v1/chat/completions \
		-H "Content-Type: application/json" \
		-d '{"model":"models/deepseek/DeepSeek-R1-Distill-Qwen-7B","messages":[{"role":"user","content":"Привет!"}],"max_tokens":50}' \
		| jq '.choices[0].message.content'

run-cli: ## Запустить CLI
	poetry run python -m src.main

run-ui: ## Запустить Streamlit UI
	poetry run streamlit run src/ui/streamlit_app.py

clean: ## Очистка
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf htmlcov/ .coverage .pytest_cache

gpu-info: ## Информация о GPU
	@nvidia-smi
