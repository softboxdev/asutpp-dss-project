"""CLI точка входа."""
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO",
           format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")
logger.add("logs/app.log", rotation="10 MB", level="DEBUG")

console = Console()
app = typer.Typer(help="СППР для проектирования архитектуры ПО АСУ ТП")


@app.command()
def check():
    """Проверка готовности системы."""
    console.print(Panel.fit("🔍 Проверка системы", style="bold blue"))
    
    results = []
    import platform
    results.append(("Python", platform.python_version(), "✅"))
    
    try:
        import torch
        if torch.cuda.is_available():
            gpu = torch.cuda.get_device_name(0)
            vram = torch.cuda.get_device_properties(0).total_memory / 1e9
            results.append(("GPU", f"{gpu} ({vram:.1f} GB)", "✅"))
        else:
            results.append(("GPU", "CUDA недоступна", "⚠️"))
    except Exception as e:
        results.append(("GPU", str(e)[:40], "❌"))
    
    try:
        from src.ai_service.local_client import get_ai_client
        client = get_ai_client()
        results.append(("AI Service", client.base_url, "✅"))
    except Exception as e:
        results.append(("AI Service", str(e)[:40], "❌"))
    
    ont = Path("data/ontology/asutp_ontology.json")
    results.append(("Онтология", str(ont) if ont.exists() else "нет", 
                    "✅" if ont.exists() else "❌"))
    
    tz = Path("data/test_examples/chemical_reactor_tz.txt")
    results.append(("Тестовое ТЗ", str(tz) if tz.exists() else "нет",
                    "✅" if tz.exists() else "⚠️"))
    
    table = Table(title="Результаты")
    table.add_column("Компонент", style="cyan")
    table.add_column("Значение", style="white")
    table.add_column("Статус", justify="center")
    for name, value, status in results:
        table.add_row(name, value, status)
    console.print(table)


@app.command()
def analyze(
    input_file: Path = typer.Option(
        Path("data/test_examples/chemical_reactor_tz.txt"),
        "--input", "-i",
    ),
    team_size: int = typer.Option(5),
    budget: float = typer.Option(10.0),
    timeline: int = typer.Option(6),
    sil: int = typer.Option(2),
    real_time: bool = typer.Option(True),
    no_ai: bool = typer.Option(False, "--no-ai"),
    full_report: bool = typer.Option(
        False, "--full-report", "-f",
        help="Сгенерировать расширенный отчёт"
    ),
):
    """Полный конвейер анализа."""
    console.print(Panel.fit("🚀 Запуск анализа", style="bold green"))
    
    if not input_file.exists():
        console.print(f"[red]❌ Файл не найден: {input_file}[/red]")
        raise typer.Exit(1)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        tz = f.read()
    
    console.print(f"📄 Документ: {len(tz)} символов")
    
    context = {
        'team_size': team_size,
        'budget_million_rub': budget,
        'timeline_months': timeline,
        'safety_level_sil': sil,
        'real_time_critical': real_time,
        'num_external_systems': 3,
        'has_scada_integration': True,
        'has_mes_integration': False,
        'num_io_points': 500,
        'num_control_loops': 25,
        'data_volume_gb_per_day': 10,
    }
    
    # Запуск конвейера
    from src.pipeline.orchestrator import ArchitectureDesignPipeline
    pipeline = ArchitectureDesignPipeline(use_ai=not no_ai)
    result = pipeline.run(tz, context, verbose=True)
    
    # === Стандартный вывод ===
    _print_entities(result.requirements.get('entities', []))
    _print_patterns(result.patterns)
    _print_quality(result.quality_assessment)
    
    # === Расширенный отчёт ===
    if full_report:
        console.print("\n" + "=" * 60)
        console.print(Panel.fit("📊 РАСШИРЕННЫЙ ОТЧЁТ", style="bold cyan"))
        console.print("=" * 60)
        
        from src.reporting import ReportBuilder
        
        builder = ReportBuilder()
        report = builder.build(result, context)
        
        # Вывод узких мест
        _print_bottlenecks(report['load']['bottlenecks'])
        
        # Вывод ресурсов
        _print_resources(report['load']['resources'])
        
        # Вывод рекомендаций
        _print_recommendations(report['load']['recommendations'])
        
        console.print(f"\n💾 Полный отчёт: {builder.output_dir}")
        
def _print_bottlenecks(bottlenecks: list):
    """Вывод узких мест."""
    console.print("\n⚠️  Узкие места:")
    if not bottlenecks:
        console.print("   [green]Не обнаружено ✅[/green]")
        return
    
    table = Table()
    table.add_column("Компонент", style="cyan")
    table.add_column("Тип", style="white")
    table.add_column("Проблемы", style="yellow")
    
    for b in bottlenecks:
        table.add_row(
            b['component'],
            b['type'],
            ', '.join(b['issues']),
        )
    console.print(table)


def _print_resources(resources: dict):
    """Вывод ресурсов."""
    console.print("\n💻 Требуемые ресурсы (с резервом 30%):")
    r = resources['with_reserve']
    
    table = Table()
    table.add_column("Ресурс", style="cyan")
    table.add_column("Значение", justify="right")
    
    table.add_row("CPU", f"{r['cpu_cores']} cores")
    table.add_row("RAM", f"{r['ram_gb']} GB")
    table.add_row("Диск/день", f"{r['disk_gb_per_day']} GB")
    table.add_row("Диск/год", f"{r['disk_gb_per_year']} GB")
    table.add_row("Сеть", f"{r['network_mbps']} Mbps")
    console.print(table)


def _print_recommendations(recs: list):
    """Вывод рекомендаций."""
    console.print("\n💡 Рекомендации:")
    
    table = Table()
    table.add_column("Приоритет", style="yellow")
    table.add_column("Компонент", style="cyan")
    table.add_column("Рекомендация")
    
    for r in recs:
        priority_style = {
            'high': '[red]HIGH[/red]',
            'medium': '[yellow]MED[/yellow]',
            'low': '[green]LOW[/green]',
        }.get(r['priority'], r['priority'])
        
        table.add_row(
            priority_style,
            r['component'],
            r['recommendation'],
        )
    console.print(table)

if __name__ == "__main__":
    app()
