import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from loguru import logger

from .topology_graph import TopologyGraphBuilder
from .architecture_examples import ArchitectureExamplesGenerator
from .typical_implementations import TypicalImplementationsLibrary
from .patterns_explorer import PatternsExplorer
from .load_calculator import LoadCalculator


class ReportBuilder:
    """Сборка полного отчёта."""
    
    def __init__(self, output_dir: str = "results/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.topology = TopologyGraphBuilder()
        self.examples_gen = ArchitectureExamplesGenerator()
        self.typical_lib = TypicalImplementationsLibrary()
        self.patterns = PatternsExplorer()
        self.load_calc = LoadCalculator()
        
        logger.info(f"ReportBuilder: {self.output_dir}")
    
    def build(
        self,
        pipeline_result,
        context: Dict,
        run_name: Optional[str] = None,
    ) -> Dict:
        """Собрать отчёт."""
        if run_name is None:
            run_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        run_dir = self.output_dir / f"run_{run_name}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Граф топологии
        if pipeline_result.architectures:
            arch = pipeline_result.architectures[0]
            G = self.topology.build_from_architecture(arch)
            topology_paths = self.topology.export_all(G, "topology")
        
        # 2. Примеры проектирования
        if pipeline_result.architectures:
            examples = self.examples_gen.generate(
                pipeline_result.architectures[0], context
            )
        else:
            examples = {}
        
        # 3. Типовые реализации
        typical = self.typical_lib.get_for_pattern(
            pipeline_result.patterns[0]['pattern']
            if pipeline_result.patterns else 'layered'
        )
        
        # 4. Паттерны
        pattern_names = [p['pattern'] for p in pipeline_result.patterns]
        patterns_info = {
            name: self.patterns.get_pattern(name)
            for name in pattern_names
        }
        
        # 5. Расчёт нагрузки
        load = self.load_calc.calculate(
            architecture=pipeline_result.architectures[0] if pipeline_result.architectures else {},
            context=context,
            simulation_results=pipeline_result.quality_assessment,
        )
        
        # === Сборка JSON-отчёта ===
        report = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'run_name': run_name,
                'context': context,
            },
            'summary': {
                'entities_count': len(pipeline_result.requirements.get('entities', [])),
                'top_pattern': pipeline_result.patterns[0]['pattern'] if pipeline_result.patterns else None,
                'quality_score': pipeline_result.quality_assessment.get('overall_score'),
                'timings': pipeline_result.timings,
            },
            'entities': pipeline_result.requirements.get('entities', [])[:50],
            'patterns': pipeline_result.patterns,
            'patterns_info': patterns_info,
            'examples': examples,
            'typical_implementations': typical,
            'load': load,
            'quality': pipeline_result.quality_assessment,
            'topology_files': {
                k: str(v) for k, v in topology_paths.items() if v
            },
            'errors': pipeline_result.errors,
        }
        
        # Сохранить JSON
        json_path = run_dir / "report.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        
        # Сохранить Markdown
        md_path = self._save_markdown(report, run_dir)
        
        logger.info(f"✅ Отчёт: {run_dir}")
        logger.info(f"   JSON: {json_path}")
        logger.info(f"   MD:   {md_path}")
        
        return report
    
    def _save_markdown(self, report: Dict, run_dir: Path) -> Path:
        """Сохранить Markdown-отчёт."""
        path = run_dir / "REPORT.md"
        
        lines = [
            "# Отчёт по проектированию архитектуры АСУ ТП",
            "",
            f"**Дата:** {report['metadata']['timestamp']}",
            f"**Run:** `{report['metadata']['run_name']}`",
            "",
            "## Резюме",
            "",
            f"- **Сущностей извлечено:** {report['summary']['entities_count']}",
            f"- **Топ-паттерн:** `{report['summary']['top_pattern']}`",
            f"- **Score качества:** {report['summary']['quality_score']:.4f}",
            f"- **Время:** {report['summary']['timings'].get('total', 0):.2f}с",
            "",
            "## Граф топологии",
            "",
            f"Файлы:",
        ]
        
        for fmt, path in report['topology_files'].items():
            lines.append(f"- `{fmt}`: `{path}`")
        
        lines.extend([
            "",
            "### Mermaid-диаграмма",
            "",
            "```mermaid",
            (run_dir / "topology.mmd").read_text(encoding='utf-8') 
                if (run_dir / "topology.mmd").exists() else "graph TD",
            "```",
            "",
            "## Архитектурные паттерны",
            "",
        ])
        
        for name, info in report['patterns_info'].items():
            lines.extend([
                f"### {info.get('name', name)}",
                "",
                f"{info.get('description', '')}",
                "",
                "**Когда использовать:**",
                *[f"- {w}" for w in info.get('when_to_use', [])],
                "",
                "**Плюсы:**",
                *[f"+ {p}" for p in info.get('pros', [])],
                "",
                "**Минусы:**",
                *[f"- {c}" for c in info.get('cons', [])],
                "",
                "**Пример:**",
                info.get('example', ''),
                "",
                f"**Специфика АСУ ТП:** {info.get('asutp_specific', '')}",
                "",
            ])
        
        lines.extend([
            "## Расчёт нагрузки",
            "",
            "### Входная нагрузка",
            "",
            "| Параметр | Значение |",
            "|----------|----------|",
        ])
        
        for k, v in report['load']['input_load'].items():
            lines.append(f"| {k} | {v} |")
        
        lines.extend([
            "",
            "### Ресурсы (с резервом 30%)",
            "",
            "| Ресурс | Значение |",
            "|--------|----------|",
        ])
        
        for k, v in report['load']['resources']['with_reserve'].items():
            lines.append(f"| {k} | {v} |")
        
        lines.extend([
            "",
            "### Рекомендуемые серверы",
            "",
            "| Роль | Кол-во | Спецификация | Причина |",
            "|------|--------|--------------|---------|",
        ])
        
        for s in report['load']['resources']['recommended_servers']:
            lines.append(f"| {s['role']} | {s['count']} | {s['spec']} | {s['reason']} |")
        
        lines.extend([
            "",
            "### Узкие места",
            "",
        ])
        
        if report['load']['bottlenecks']:
            for b in report['load']['bottlenecks']:
                lines.append(f"- **{b['component']}** ({b['type']}): {', '.join(b['issues'])}")
        else:
            lines.append("- Узких мест не обнаружено ✅")
        
        lines.extend([
            "",
            "## Типовые реализации",
            "",
        ])
        
        for impl in report['typical_implementations']:
            lines.extend([
                f"### {impl['name']}",
                "",
                f"{impl['description']}",
                "",
                f"**Для чего:** {', '.join(impl['typical_for'])}",
                "",
                f"**Стандарты:** {', '.join(impl['standards'])}",
                "",
                impl['implementation'],
                "",
            ])
        
        path.write_text('\n'.join(lines), encoding='utf-8')
        return path