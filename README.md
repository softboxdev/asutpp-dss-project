# Остановить все процессы
```bash
# Убедитесь, что DeepSeek остановлен
make stop-deepseek 2>/dev/null || pkill -f vllm

# Выйдите из виртуального окружения
exit
```

# Диагностика среды

```bash
echo "=== 1. GPU устройства ==="
lspci | grep -i -E "vga|3d|display"

echo ""
echo "=== 2. Драйвер NVIDIA ==="
dpkg -l | grep -i nvidia | head -10

echo ""
echo "=== 3. Модуль nvidia ==="
lsmod | grep nvidia

echo ""
echo "=== 4. Устройства /dev/nvidia* ==="
ls -la /dev/nvidia* 2>&1

echo ""
echo "=== 5. Тип системы ==="
systemd-detect-virt

echo ""
echo "=== 6. Ядро ==="
uname -r

echo ""
echo "=== 7. Рекомендуемые драйверы ==="
ubuntu-drivers devices 2>&1

echo ""
echo "=== 8. Ubuntu версия ==="
lsb_release -a
```
# Проверка видеокарты
```bash
nvidia-smi
# Должны увидеть таблицу с GPU.
```

# Если драйверы не установлены 
# Установка драйверов. Установка NVIDIA Driver 
```bash
# 1. Удалите возможные остатки
sudo apt remove --purge '^nvidia-.*' -y
sudo apt autoremove -y

# 2. Добавьте PPA
sudo add-apt-repository ppa:graphics-drivers/ppa -y
sudo apt update

# 3. Установите рекомендуемый драйвер
ubuntu-drivers devices
# Проверьте, что nouveau не активен
lsmod | grep nouveau
sudo apt install -y nvidia-driver-595-open
sudo dkms status

# если модуль не загрузился - статус built или пусто
# Установите headers ядра (если ещё нет)
sudo apt install -y linux-headers-$(uname -r)

# Пересоберите DKMS
sudo dkms autoinstall

# Проверьте снова
sudo dkms status

# 4. Перезагрузка
sudo reboot

# 5. После перезагрузки проверка
nvidia-smi
```
# Установка CUDA Toolkit

```bash
# Скачивание установщика
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt update

# Установка CUDA 12.1
sudo apt install -y cuda-toolkit-12-1

# Добавление в PATH
echo 'export PATH=/usr/local/cuda-12.1/bin:$PATH' >> ~/.bashrc
echo 'export LD_LIBRARY_PATH=/usr/local/cuda-12.1/lib64:$LD_LIBRARY_PATH' >> ~/.bashrc
source ~/.bashrc

# Проверка
nvcc --version
# Должен показать версию driver компилятора CUDA 
```

# Установка ДОКЕР компилятора

```bash
# Установка Docker
curl -fsSL https://get.docker.com | sh

# Добавление вашего пользователя в группу docker
sudo usermod -aG docker $USER

# Применение изменений (или перезайдите в систему)
newgrp docker

# Проверка
docker --version
```

# Установка NVIDIA Container Toolkit

```bash
# Добавление репозитория
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Установка
sudo apt update
sudo apt install -y nvidia-container-toolkit
sudo systemctl restart docker

# Проверка GPU в Docker
docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

# УСТАНОВКА PYTHON И ИНСТРУМЕНТОВ
```bash
# Добавление репозитория
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt update

# Установка Python 3.10
sudo apt install -y python3.12 python3.12-venv python3.12-dev python3-pip

# Проверка
python3.12 --version
```

# Установка Poetry (менеджер зависимостей)
```bash
# Установка Poetry
curl -sSL https://install.python-poetry.org | python3.12 -

# Добавление в PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Проверка
poetry --version
```

# Установка Git
```bash
# Проверка наличия
git --version

# Если не установлен
sudo apt install -y git

# Настройка
git config --global user.name "Ваше Имя"
git config --global user.email "your.email@example.com"
```
#  Установка базовых утилит
```bash
sudo apt install -y \
    build-essential \
    curl \
    wget \
    vim \
    htop \
    tmux \
    jq \
    unzip \
    tree
```

# Создайте рабочую директорию
```bash
# Переход в домашнюю директорию
cd ~

# Создание директории проектов
mkdir -p ~/projects
cd ~/projects

# Создание директории проекта
mkdir -p asutp-dss-local
cd asutp-dss-local

# Проверка текущей директории
pwd
```

# Создайте структуру проекта
```bash
mkdir -p \
    src/{core,ml/{dacie,classifier,generator,optimizer,evaluator,xai},dsal,deepseek/{prompts,parsers},pipeline,storage,ui} \
    tests/{unit,integration,e2e} \
    configs/{model_configs,dsal_configs,deployment_configs} \
    data/{raw,processed,synthetic,ontology,test_examples} \
    models/{deepseek,dacie,classifier,generator,optimizer,production} \
    notebooks/{experiments,analysis} \
    scripts \
    docker/{prometheus,grafana} \
    logs \
    results \
    docs/{architecture,api,user_guide}

# Создание __init__.py во всех папках src
find src -type d -exec touch {}/__init__.py \;

# Проверка структуры
tree -L 2 -I '__pycache__|*.pyc|.git'
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
# Активация виртуального окружения

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

# .env:
```
cat > .env << 'EOF'
# ============================================================
# КОНФИГУРАЦИЯ ПОЛНОСТЬЮ ЛОКАЛЬНОГО ПРОЕКТА
# ============================================================
OLLAMA_PUBLIC_KEY=ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICh4GFRnwHRv1WWV/OwV/2aDLy5dkoy1Ao1zldqrzBHF
DEEPSEEK_HOST=localhost
DEEPSEEK_PORT=11434
DEEPSEEK_MODEL_PATH=deepseek-r1:7b


# ============================================================
# КОНФИГУРАЦИЯ ПОЛНОСТЬЮ ЛОКАЛЬНОГО ПРОЕКТА
# ============================================================

# DeepSeek (локальный)
# DEEPSEEK_MODEL_PATH=models/deepseek/DeepSeek-R1-Distill-Qwen-7B
# DEEPSEEK_HOST=localhost
# DEEPSEEK_PORT=8001
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


# Полный сценарий запуска
```bash
# 1. Клонирование / создание проекта
cd ~/projects/asutp-dss-local

# 2. Установка зависимостей
poetry install

# 3. Настройка окружения
cp .env.example .env
vim .env  # при необходимости

# 4. Загрузка модели DeepSeek
make download-model

# 5. Запуск DeepSeek сервера (в фоне)
make start-deepseek-bg

# 6. Ожидание загрузки модели (2-5 минут)
sleep 180
make check-deepseek

# 7. Подготовка данных
poetry run python scripts/prepare_data.py

# 8. Тестовый запуск
make run-cli

# 9. Запуск UI
make run-ui
# Открыть http://localhost:8501
```

# Пример использования
```python
"""
Полный пример работы с локальной DeepSeek.
"""
import sys
sys.path.insert(0, '/home/user/projects/asutp-dss-local')

from src.pipeline.orchestrator import ArchitectureDesignPipeline
from src.dsal.orchestrator import DSALOrchestrator
from src.deepseek.local_client import get_deepseek_client

# 1. Проверка DeepSeek
client = get_deepseek_client()
print("DeepSeek доступен")

# 2. Тестовый запрос
response = client.generate(
    "Извлеки сущности: Система должна контролировать температуру 150-200°C",
    max_tokens=512
)
print(f"DeepSeek ответил:\n{response[:500]}")

# 3. Полный конвейер
pipeline = ArchitectureDesignPipeline()

with open('data/test_examples/chemical_reactor_tz.txt', 'r') as f:
    tz_text = f.read()

context = {
    'team_size': 8,
    'budget_million_rub': 15,
    'timeline_months': 8,
    'real_time_critical': True,
    'safety_level_sil': 2,
}

result = pipeline.run(tz_text, context, verbose=True)

# 4. DSAL-обучение
dsal = DSALOrchestrator(main_model=None)  # заменить на реальную модель

labeled_data = [{'text': 'пример', 'entities': []}]
unlabeled_data = [tz_text]

dsal.run_full_cycle(
    labeled_data=labeled_data,
    unlabeled_data=unlabeled_data,
    epochs=5
)

print("✅ Всё работает полностью локально")
```