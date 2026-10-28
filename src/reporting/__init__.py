"""Модуль расширенного отчёта."""
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
from .report_builder import ReportBuilder, ExtendedReportBuilder

__all__ = [
    'ReportSection',
    'TopologyGraphBuilder',
    'ComponentModelBuilder',
    'TechStackRecommender',
    'ArchitectureExamplesGenerator',
    'TypicalImplementationsLibrary',
    'PatternsExplorer',
    'LoadCalculator',
    'WorkPlanBuilder',
    'EffortEstimator',
    'RoadmapBuilder',
    'BudgetEstimator',
    'TeamPlanner',
    'RiskAssessor',
    'TraceabilityBuilder',
    'ComplianceChecker',
    'TestPlanBuilder',
    'DeploymentPlanner',
    'SLAMetricsBuilder',
    'ReportBuilder',
    'ExtendedReportBuilder',
]