#!/usr/bin/env python3
"""
Генератор тестовых ТЗ АСУ ТП через Ollama.

Использование:
    # 1. Одно ТЗ (по умолчанию — химический реактор)
    poetry run python scripts/generate_test_tz.py

    # 2. Конкретная отрасль
    poetry run python scripts/generate_test_tz.py --domain oil_gas

    # 3. Несколько отраслей
    poetry run python scripts/generate_test_tz.py --domains chemical,oil_gas,power

    # 4. Все отрасли
    poetry run python scripts/generate_test_tz.py --all

    # 5. Другая модель / длина
    poetry run python scripts/generate_test_tz.py --model deepseek-r1:1.5b --min-chars 1500

    # 6. Без сохранения (только вывод)
    poetry run python scripts/generate_test_tz.py --dry-run
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from loguru import logger

# Добавить корень проекта в path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.ai_service.local_client import AIClient


console = Console()

# Настройка логирования
logger.remove()
logger.add(
    sys.stdout,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
)
logger.add("logs/tz_generator.log", rotation="10 MB", level="DEBUG")


# ============================================================
# Отрасли и шаблоны
# ============================================================

DOMAINS: Dict[str, Dict[str, str]] = {
    "chemical": {
        "name": "Химическая промышленность",
        "object": "установка гидроочистки дизельного топлива производительностью 2 млн тонн в год",
        "parameters": "температура 150-200°C, давление 10-15 атм, расход 50-100 м³/ч",
        "safety": "SIL 2 согласно IEC 61508",
        "protocols": "OPC UA, Modbus TCP, Profinet",
        "scada": "Siemens WinCC",
        "io_points": 500,
        "control_loops": 25,
        "performance": "время отклика не более 100 мс, пропускная способность не менее 1000 сигналов/с",
        "reliability": "доступность 99.95%, MTBF 10000 часов, горячее резервирование контроллеров",
    },
    "oil_gas": {
        "name": "Нефтегазовая промышленность",
        "object": "установка подготовки нефти производительностью 5 млн тонн в год",
        "parameters": "давление 5-25 атм, температура 20-80°C, уровень жидкости 30-70%",
        "safety": "SIL 3 согласно IEC 61511",
        "protocols": "OPC UA, Modbus RTU, HART",
        "scada": "Emerson DeltaV",
        "io_points": 800,
        "control_loops": 40,
        "performance": "время отклика не более 150 мс, пропускная способность не менее 2000 сигналов/с",
        "reliability": "доступность 99.99%, MTBF 20000 часов, горячее резервирование по схеме 2oo3",
    },
    "power": {
        "name": "Энергетика",
        "object": "энергоблок ТЭЦ мощностью 200 МВт",
        "parameters": "давление пара 100-140 атм, температура 500-560°C, частота 50 Гц",
        "safety": "SIL 2 согласно IEC 61508",
        "protocols": "OPC UA, IEC 61850, Modbus TCP",
        "scada": "АББ 800xA",
        "io_points": 1200,
        "control_loops": 60,
        "performance": "время отклика не более 50 мс, пропускная способность не менее 5000 сигналов/с",
        "reliability": "доступность 99.98%, MTBF 15000 часов, резервирование контроллеров и сетей",
    },
    "food": {
        "name": "Пищевая промышленность",
        "object": "линия производства молочной продукции производительностью 100 тонн в сутки",
        "parameters": "температура 2-95°C, давление 1-10 атм, влажность 40-80%",
        "safety": "SIL 1 согласно IEC 61508",
        "protocols": "OPC UA, Modbus TCP, Ethernet/IP",
        "scada": "Wonderware InTouch",
        "io_points": 300,
        "control_loops": 15,
        "performance": "время отклика не более 200 мс, пропускная способность не менее 500 сигналов/с",
        "reliability": "доступность 99.9%, MTBF 8000 часов, резервирование критических узлов",
    },
    "water": {
        "name": "Водоснабжение",
        "object": "станция водоподготовки производительностью 100 000 м³/сутки",
        "parameters": "давление 2-8 атм, расход 500-2000 м³/ч, мутность 0.5-5 NTU",
        "safety": "SIL 1 согласно IEC 61508",
        "protocols": "OPC UA, Modbus TCP, IEC 60870-5-104",
        "scada": "Schneider ClearSCADA",
        "io_points": 400,
        "control_loops": 20,
        "performance": "время отклика не более 200 мс, пропускная способность не менее 800 сигналов/с",
        "reliability": "доступность 99.9%, MTBF 12000 часов, резервирование насосных станций",
    },
    "mining": {
    "name": "Горнодобывающая промышленность",
    "object": "обогатительная фабрика производительностью 10 млн тонн руды в год",
    "parameters": "расход пульпы 500-1500 м³/ч, плотность 1.2-1.5 т/м³, крупность 0-10 мм",
    "safety": "SIL 2 согласно IEC 61508",
    "protocols": "OPC UA, Modbus TCP, Profibus",
    "scada": "Rockwell FactoryTalk",
    "io_points": 600,
    "control_loops": 30,
    "performance": "время отклика не более 120 мс",
    "reliability": "доступность 99.9%, MTBF 15000 часов",
    }
}


# ============================================================
# Промпты
# ============================================================

SYSTEM_PROMPT = """Ты — опытный инженер-проектировщик АСУ ТП.
Твоя задача — написать реалистичное техническое задание на 
автоматизированную систему управления технологическим процессом (АСУ ТП).

Требования к ТЗ:
- Структурированный документ с разделами (1., 1.1., 1.1.1. и т.д.)
- Техническая терминология
- Конкретные числа и параметры
- Соответствие стандартам IEC, ГОСТ
- Объём: ~1500-2500 символов

Отвечай ТОЛЬКО текстом ТЗ, без markdown, без пояснений."""


def build_tz_prompt(domain: str, min_chars: int = 1500) -> str:
    """Сформировать промпт для генерации ТЗ."""
    d = DOMAINS[domain]
    
    return f"""Напиши техническое задание на АСУ ТП для объекта:

**Отрасль:** {d['name']}
**Объект:** {d['object']}
**Технологические параметры:** {d['parameters']}
**Требования безопасности:** {d['safety']}
**Протоколы:** {d['protocols']}
**SCADA:** {d['scada']}
**Точек ввода-вывода:** {d['io_points']}
**Регулирующих контуров:** {d['control_loops']}
**Производительность:** {d['performance']}
**Надёжность:** {d['reliability']}

Структура ТЗ:
1. ОБЩИЕ ПОЛОЖЕНИЯ
   1.1. Назначение системы
   1.2. Цели создания
2. ТРЕБОВАНИЯ К СИСТЕМЕ
   2.1. Функциональные требования
   2.2. Требования к безопасности
   2.3. Требования к производительности
   2.4. Требования к надёжности
3. ТРЕБОВАНИЯ К ИНТЕРФЕЙСАМ
   3.1. Интеграция с SCADA
   3.2. Интеграция с MES
   3.3. Интеграция с ERP
4. ТРЕБОВАНИЯ К ТЕХНИЧЕСКОМУ ОБЕСПЕЧЕНИЮ

Объём: не менее {min_chars} символов.
Используй русский язык и профессиональную терминологию.
Только текст ТЗ, без комментариев."""


# ============================================================
# Генерация
# ============================================================

def generate_tz(
    domain: str,
    client: AIClient,
    min_chars: int = 1500,
    temperature: float = 0.3,
    max_tokens: int = 4096,
) -> str:
    """Сгенерировать одно ТЗ."""
    if domain not in DOMAINS:
        raise ValueError(f"Неизвестная отрасль: {domain}")
    
    d = DOMAINS[domain]
    console.print(f"\n[cyan]Генерация ТЗ для:[/cyan] {d['name']}")
    console.print(f"  Объект: {d['object']}")
    
    prompt = build_tz_prompt(domain, min_chars)
    
    try:
        response = client.generate(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=temperature,
            max_tokens=max_tokens,
            use_cache=False,   # всегда генерируем заново
        )
        
        # Очистить markdown, если есть
        text = _clean_response(response)
        
        console.print(f"  [green]✅ Получено {len(text)} символов[/green]")
        return text
    
    except Exception as e:
        logger.error(f"Ошибка генерации: {e}")
        raise


def _clean_response(text: str) -> str:
    """Удалить markdown-обёртку и лишние пробелы."""
    text = text.strip()
    
    # Удалить ```markdown / ```text / ``` в начале и конце
    if text.startswith("```"):
        lines = text.split('\n')
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = '\n'.join(lines)
    
    # Удалить XML-теги thinking (если reasoning-модель)
    import re
    text = re.sub(r'<\|?thinking\|?>.*?<\|?/thinking\|?>', '', text, flags=re.DOTALL)
    
    return text.strip()


# ============================================================
# Сохранение
# ============================================================

def save_tz(domain: str, text: str, output_dir: Path) -> Path:
    """Сохранить ТЗ в файл."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Имя: {domain}_tz.txt
    filename = f"{domain}_tz.txt"
    path = output_dir / filename
    
    # Заголовок с метаданными
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    header = f"""# Техническое задание на АСУ ТП
# Отрасль: {DOMAINS[domain]['name']}
# Объект: {DOMAINS[domain]['object']}
# Сгенерировано: {timestamp}
# Генератор: Ollama / {DOMAINS[domain].get('model', 'deepseek-r1:7b')}
# ============================================================

"""
    
    path.write_text(header + text, encoding='utf-8')
    return path


# ============================================================
# CLI
# ============================================================

def print_available_domains():
    """Вывести список отраслей."""
    table = Table(title="Доступные отрасли")
    table.add_column("Ключ", style="cyan")
    table.add_column("Отрасль", style="white")
    table.add_column("Объект", style="dim")
    
    for key, d in DOMAINS.items():
        table.add_row(key, d['name'], d['object'][:50])
    
    console.print(table)


def main(
    domain: str = typer.Option(
        "chemical", "--domain", "-d",
        help="Отрасль (chemical, oil_gas, power, food, water)"
    ),
    domains: Optional[str] = typer.Option(
        None, "--domains",
        help="Несколько отраслей через запятую"
    ),
    all_domains: bool = typer.Option(
        False, "--all", "-a",
        help="Сгенерировать для всех отраслей"
    ),
    model: Optional[str] = typer.Option(
        None, "--model", "-m",
        help="Модель Ollama (по умолчанию из .env)"
    ),
    output_dir: str = typer.Option(
        "data/test_examples", "--output", "-o",
        help="Директория сохранения"
    ),
    min_chars: int = typer.Option(
        1500, "--min-chars",
        help="Минимальная длина ТЗ (символов)"
    ),
    temperature: float = typer.Option(
        0.3, "--temperature", "-t",
        help="Температура генерации"
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run",
        help="Не сохранять, только вывести"
    ),
    show_list: bool = typer.Option(
        False, "--list", "-l",
        help="Показать доступные отрасли"
    ),
):
    """Генератор тестовых ТЗ АСУ ТП через Ollama."""
    
    if show_list:
        print_available_domains()
        return
    
    # Определить список отраслей
    if all_domains:
        targets = list(DOMAINS.keys())
    elif domains:
        targets = [d.strip() for d in domains.split(',')]
    else:
        targets = [domain]
    
    # Проверить
    for t in targets:
        if t not in DOMAINS:
            console.print(f"[red]❌ Неизвестная отрасль: {t}[/red]")
            console.print("Доступные: " + ", ".join(DOMAINS.keys()))
            raise typer.Exit(1)
    
    # Заголовок
    console.print(Panel.fit(
        f"🚀 Генератор ТЗ\n"
        f"Модель: {model or 'из .env'}\n"
        f"Отрасли: {', '.join(targets)}\n"
        f"Мин. длина: {min_chars} символов",
        style="bold blue"
    ))
    
    # Подключиться к Ollama
    try:
        client = AIClient(model_name=model)
        console.print(f"[green]✅ Ollama: {client.base_url}[/green]")
    except Exception as e:
        console.print(f"[red]❌ Ollama недоступен: {e}[/red]")
        console.print("Запустите: sudo systemctl start ollama")
        raise typer.Exit(1)
    
    # Генерация
    output_path = Path(output_dir)
    results = []
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task = progress.add_task("Генерация...", total=len(targets))
        
        for i, dom in enumerate(targets):
            progress.update(
                task,
                description=f"Генерация [{i+1}/{len(targets)}]: {DOMAINS[dom]['name'][:30]}",
            )
            
            try:
                text = generate_tz(
                    domain=dom,
                    client=client,
                    min_chars=min_chars,
                    temperature=temperature,
                )
                
                if dry_run:
                    # Только вывод
                    console.print(f"\n[yellow]{'='*60}[/yellow]")
                    console.print(f"[bold]{dom}[/bold] ({len(text)} символов)")
                    console.print(f"[yellow]{'='*60}[/yellow]")
                    console.print(text[:500] + "\n...")
                else:
                    path = save_tz(dom, text, output_path)
                    console.print(f"  [green]💾 {path}[/green]")
                    results.append({
                        'domain': dom,
                        'path': str(path),
                        'chars': len(text),
                    })
            
            except Exception as e:
                console.print(f"  [red]❌ {dom}: {e}[/red]")
            
            progress.update(task, advance=1)
    
    # Итоги
    if results and not dry_run:
        console.print("\n" + "=" * 60)
        table = Table(title="Итоги генерации")
        table.add_column("Отрасль", style="cyan")
        table.add_column("Файл", style="green")
        table.add_column("Размер", justify="right")
        
        for r in results:
            table.add_row(
                r['domain'],
                Path(r['path']).name,
                f"{r['chars']:,} символов",
            )
        
        console.print(table)
        
        # Быстрый тест первого файла
        console.print("\n[bold]Быстрая проверка:[/bold]")
        console.print(f"  cat {results[0]['path']} | head -20")
        console.print(f"  poetry run python -m src.main analyze --input {results[0]['path']}")


if __name__ == "__main__":
    typer.run(main)