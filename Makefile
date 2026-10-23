.PHONY: help install start-ai stop-ai check-ai test-ai run-cli run-ui check clean

GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
RESET  := $(shell tput -Txterm sgr0)

help:
	@echo "${GREEN}Команды:${RESET}"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  ${YELLOW}%-20s${RESET} %s\n", $$1, $$2}'

install: ## Установить зависимости
	poetry install

start-ai: ## Запустить Ollama
	sudo systemctl start ollama
	@echo "Ollama запущен"

stop-ai: ## Остановить Ollama
	sudo systemctl stop ollama

check-ai: ## Проверить Ollama
	@curl -s http://localhost:11434/v1/models | jq -r '.data[].id' || \
		echo "Ollama недоступен"

test-ai: ## Тест запроса
	@curl -s -X POST http://localhost:11434/v1/chat/completions \
		-H "Content-Type: application/json" \
		-d '{"model":"deepseek-r1:7b","messages":[{"role":"user","content":"Скажи привет"}],"max_tokens":20}' \
		| jq -r '.choices[0].message.content'

run-cli: ## CLI
	poetry run python -m src.main analyze

analyze: ## Запустить анализ
	poetry run python -m src.main analyze

run-ui: ## Streamlit UI
	poetry run streamlit run src/ui/streamlit_app.py

run-api: ## FastAPI
	poetry run uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --reload

check: ## Проверка системы
	poetry run python -m src.main check

clean: ## Очистка
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
	rm -rf .pytest_cache htmlcov .coverage
