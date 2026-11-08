"""Сборка полного отчёта."""
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
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
    """Базовый отчёт (6 секций)."""
    
    def __init__(self, output_dir: str = "results/reports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Секции
        self.sections = [
            TopologyGraphBuilder(self.output_dir),
            ArchitectureExamplesGenerator(self.output_dir),
            TypicalImplementationsLibrary(self.output_dir),
            PatternsExplorer(self.output_dir),
            LoadCalculator(self.output_dir),
        ]
        
        logger.info(f"ReportBuilder: {self.output_dir}")
    
    def build(self, pipeline_result, context: Dict, run_name: str = None) -> Dict:
        """Построить базовый отчёт."""
        if run_name is None:
            run_name = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        run_dir = self.output_dir / f"run_{run_name}"
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Меняем output_dir для секций
        for section in self.sections:
            section.output_dir = run_dir
        
        report = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'run_name': run_name,
                'context': context,
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
        
        # Секции
        for section in self.sections:
            try:
                logger.info(f"  {section.title}...")
                report[section.name] = section.build(pipeline_result, context)
            except Exception as e:
                logger.error(f"  ❌ {section.name}: {e}")
                report[section.name] = {'error': str(e)}
        
        # Сохранить
        self._save_json(report, run_dir)
        self._save_markdown(report, run_dir, base=True)
        
        logger.info(f"✅ Отчёт: {run_dir}")
        return report
    
    def _save_json(self, report: Dict, run_dir: Path):
        path = run_dir / "report.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)
    
    def _save_markdown(self, report: Dict, run_dir: Path, base: bool = True):
        lines = [
            "# Отчёт по проектированию архитектуры АСУ ТП",
            "",
            f"**Дата:** {report['metadata']['timestamp']}",
            f"**Run:** `{report['metadata']['run_name']}`",
            "",
            "## Резюме",
            "",
            f"- **Сущностей:** {report['summary']['entities_count']}",
            f"- **Топ-паттерн:** `{report['summary']['top_pattern']}`",
            f"- **Score:** {report['summary']['quality_score']:.4f}",
            f"- **Время:** {report['summary']['timings'].get('total', 0):.2f}с",
            "",
        ]
        
        for section in self.sections:
            data = report.get(section.name, {})
            if data and 'error' not in data:
                lines.extend(["---", "", f"# {section.title}", ""])
                lines.append(section.to_markdown(data))
        
        path = run_dir / "REPORT.md"
        path.write_text('\n'.join(lines), encoding='utf-8')


class ExtendedReportBuilder(ReportBuilder):
    """Расширенный отчёт (18 секций)."""
    
    def __init__(self, output_dir: str = "results/reports"):
        super().__init__(output_dir)
        
        # Добавить остальные секции
        self.sections.extend([
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
        ])
        
        # Сортировка по порядку
        self.sections.sort(key=lambda s: s.order)
        
        logger.info(f"ExtendedReportBuilder: {len(self.sections)} секций")
    
    def build(self, pipeline_result, context: Dict, run_name: str = None) -> Dict:
        """Построить полный отчёт."""
        report = super().build(pipeline_result, context, run_name)
        
        # Пересохранить с полным Markdown
        run_dir = self.output_dir / f"run_{report['metadata']['run_name']}"
        self._save_markdown(report, run_dir, base=False)
        
        return report
