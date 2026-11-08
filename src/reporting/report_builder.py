"""Сборка полного отчёта на основе секций."""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
from loguru import logger

from .base import ReportSection
from .topology_graph import TopologyGraphBuilder
from .component_model import ComponentModelBuilder
from .tech_stack import TechStackRecommender
from .architecture_examples import ArchitectureExamplesGenerator
from .typical_implementations import TypicalImplementationsLibrary
from .patterns_explorer import PatternsExplorer
from .load_calculator import LoadCalculator
from .work_plan import WorkPlanBuilder
from .effort_estimator import EffortEstimator
from .roadmap import RoadmapBuilder
from .budget_estimator import BudgetEstimator
from .team_plan import TeamPlanner
from .risk_assessor import RiskAssessor
from .traceability import TraceabilityBuilder
from .compliance import ComplianceChecker
from .test_plan import TestPlanBuilder
from .deployment_plan import DeploymentPlanner
from .sla_metrics import SLAMetricsBuilder


class ReportBuilder:
    """Базовый отчёт (5-6 секций)."""
    
    def __init__(self, output_dir: str = "results/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Базовые секции
        self.sections: List[ReportSection] = [
            TopologyGraphBuilder(self.output_dir),
            ArchitectureExamplesGenerator(self.output_dir),
            TypicalImplementationsLibrary(self.output_dir),
            PatternsExplorer(self.output_dir),
            LoadCalculator(self.output_dir),
        ]
        
        logger.info(f"ReportBuilder: {len(self.sections)} секций")
    
    def build(
        self,
        pipeline_result,
        context: Dict,
        run_name: Optional[str] = None,
    ) -> Dict:
        """Построить отчёт."""
        if run_name is None:
            run_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        run_dir = self.output_dir / f"run_{run_name}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Меняем output_dir у секций на run_dir
        for section in self.sections:
            section.output_dir = run_dir
        
        # Базовый отчёт
        report: Dict = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'run_name': run_name,
                'context': context,
                'sections_count': len(self.sections),
            },
            'summary': {
                'entities_count': len(pipeline_result.requirements.get('entities', [])),
                'top_pattern': pipeline_result.patterns[0]['pattern'] 
                    if pipeline_result.patterns else None,
                'quality_score': pipeline_result.quality_assessment.get('overall_score'),
                'timings': pipeline_result.timings,
            },
            'entities': pipeline_result.requirements.get('entities', [])[:50],
            'patterns': pipeline_result.patterns,
            'quality': pipeline_result.quality_assessment,
            'errors': pipeline_result.errors,
        }
        
        # Строим все секции
        for section in self.sections:
            try:
                logger.info(f"  Секция: {section.title}")
                data = section.build(pipeline_result, context)
                report[section.name] = data
            except Exception as e:
                logger.exception(f"  ❌ Ошибка в {section.name}: {e}")
                report[section.name] = {'error': str(e)}
        
        # Сохраняем JSON и Markdown
        self._save_json(report, run_dir)
        self._save_markdown(report, run_dir)
        
        logger.info(f"✅ Отчёт: {run_dir}")
        return report
    
    def _save_json(self, report: Dict, run_dir: Path):
        """Сохранить JSON."""
        path = run_dir / "report.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
        logger.info(f"   JSON: {path}")
    
    def _save_markdown(self, report: Dict, run_dir: Path):
        """Сохранить Markdown."""
        lines = self._markdown_header(report)
        
        # Каждая секция в своём формате
        for section in self.sections:
            data = report.get(section.name, {})
            if not data or 'error' in data:
                continue
            
            lines.append(f"## {section.title}")
            lines.append("")
            
            try:
                md = section.to_markdown(data)
                if md:
                    lines.append(md)
                else:
                    lines.append("```json")
                    lines.append(json.dumps(data, ensure_ascii=False, indent=2, default=str)[:3000])
                    lines.append("```")
            except Exception as e:
                lines.append(f"*Ошибка экспорта: {e}*")
            
            lines.append("")
        
        path = run_dir / "REPORT.md"
        path.write_text('\n'.join(lines), encoding='utf-8')
        logger.info(f"   MD: {path}")
    
    def _markdown_header(self, report: Dict) -> List[str]:
        """Заголовок Markdown."""
        s = report['summary']
        return [
            "# Отчёт по проектированию архитектуры АСУ ТП",
            "",
            f"**Дата:** {report['metadata']['timestamp']}",
            f"**Run:** `{report['metadata']['run_name']}`",
            f"**Секций:** {report['metadata']['sections_count']}",
            "",
            "## Резюме",
            "",
            f"- **Сущностей:** {s['entities_count']}",
            f"- **Топ-паттерн:** `{s.get('top_pattern', '—')}`",
            f"- **Score:** {s.get('quality_score', 0):.4f}",
            f"- **Время:** {s.get('timings', {}).get('total', 0):.2f}с",
            "",
            "---",
            "",
        ]


class ExtendedReportBuilder(ReportBuilder):
    """Расширенный отчёт (18 секций)."""
    
    def __init__(self, output_dir: str = "results/reports"):
        super().__init__(output_dir)
        
        # Добавляем расширенные секции
        extended = [
            ComponentModelBuilder(self.output_dir),
            TechStackRecommender(self.output_dir),
            WorkPlanBuilder(self.output_dir),
            EffortEstimator(self.output_dir),
            RoadmapBuilder(self.output_dir),
            BudgetEstimator(self.output_dir),
            TeamPlanner(self.output_dir),
            RiskAssessor(self.output_dir),
            TraceabilityBuilder(self.output_dir),
            ComplianceChecker(self.output_dir),
            TestPlanBuilder(self.output_dir),
            DeploymentPlanner(self.output_dir),
            SLAMetricsBuilder(self.output_dir),
        ]
        
        self.sections.extend(extended)
        
        # Сортируем по order
        self.sections.sort(key=lambda s: getattr(s, 'order', 999))
        
        logger.info(f"ExtendedReportBuilder: {len(self.sections)} секций")
