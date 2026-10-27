"""Оркестратор 6-этапного конвейера."""
import time
from dataclasses import dataclass, field
from typing import Dict, List, Any
from loguru import logger

from src.ml.dacie.entity_extractor import DACIE
from src.ml.classifier.xgboost_model import PatternClassifier
from src.ml.generator.vae_generator import ArchitectureVAE
from src.ml.optimizer.optimizer import TopologyOptimizer, optimize_placement
from src.ml.evaluator.simulator import evaluate_architecture
from src.ml.xai.shap_analyzer import ArchitectureExplainer


@dataclass
class PipelineResult:
    requirements: Dict = field(default_factory=dict)
    patterns: List[Dict] = field(default_factory=list)
    graph: Any = None
    architectures: List[Dict] = field(default_factory=list)
    optimized_config: Dict = field(default_factory=dict)
    quality_assessment: Dict = field(default_factory=dict)
    explanation: Dict = field(default_factory=dict)
    timings: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class ArchitectureDesignPipeline:
    def __init__(self, use_ai: bool = True):
        logger.info("=" * 60)
        logger.info("Инициализация конвейера")
        logger.info("=" * 60)
        
        self.dacie = DACIE(use_ai=use_ai)
        self.classifier = PatternClassifier()
        self.vae = ArchitectureVAE()
        self.topology_optimizer = TopologyOptimizer()
        self.explainer = ArchitectureExplainer(self.classifier)
        
        logger.info("=" * 60)
        logger.info("Все компоненты готовы")
        logger.info("=" * 60)
    
    def run(self, document_text: str, context: Dict,
            verbose: bool = True) -> PipelineResult:
        result = PipelineResult()
        timings = {}
        total_start = time.time()
        
        # Шаг 1
        if verbose:
            logger.info("Шаг 1/6: NLP-анализ (DACIE)")
        t0 = time.time()
        try:
            dacie_out = self.dacie.process(document_text)
            result.requirements = dacie_out
            result.graph = dacie_out.get('graph')
            timings['step1_nlp'] = time.time() - t0
            if verbose:
                logger.info(f"  ✅ {timings['step1_nlp']:.2f}с | "
                           f"сущностей: {len(dacie_out.get('entities', []))}")
        except Exception as e:
            result.errors.append(f"Шаг 1: {e}")
            logger.exception(f"  ❌ {e}")
            return result
        
        # Шаг 2
        if verbose:
            logger.info("Шаг 2/6: Классификация паттернов")
        t0 = time.time()
        try:
            patterns = self.classifier.classify(
                result.requirements.get('entities', []), context,
            )
            result.patterns = patterns
            timings['step2_classification'] = time.time() - t0
            if verbose:
                logger.info(f"  ✅ {timings['step2_classification']:.2f}с | "
                           f"топ: {patterns[0]['pattern']}")
        except Exception as e:
            result.errors.append(f"Шаг 2: {e}")
            logger.exception(f"  ❌ {e}")
            return result
        
        # Шаг 3
        if verbose:
            logger.info("Шаг 3/6: Графовое моделирование")
        t0 = time.time()
        try:
            architectures = self.vae.generate(patterns[0], context, n_samples=5)
            best_arch = architectures[0]
            initial_graph = self.vae.to_graph(best_arch)
            optimized_graph = self.topology_optimizer.optimize(
                initial_graph,
                {'real_time': context.get('real_time_critical', False)},
                num_iterations=20,
            )
            result.architectures = architectures
            result.graph = optimized_graph
            timings['step3_graph'] = time.time() - t0
            if verbose:
                logger.info(f"  ✅ {timings['step3_graph']:.2f}с | "
                           f"узлов: {optimized_graph.number_of_nodes()}")
        except Exception as e:
            result.errors.append(f"Шаг 3: {e}")
            logger.exception(f"  ❌ {e}")
            return result
        
        # Шаг 4
        if verbose:
            logger.info("Шаг 4/6: Оптимизация размещения")
        t0 = time.time()
        try:
            components = [
                {'id': n, 'latency': float(
                    optimized_graph.nodes[n].get('latency', 10)
                )}
                for n in optimized_graph.nodes()
            ]
            nodes = [
                {'id': 'server_1', 'cost_rub': 500000,
                 'latency_ms': 5, 'failure_rate': 0.001},
                {'id': 'server_2', 'cost_rub': 800000,
                 'latency_ms': 3, 'failure_rate': 0.0005},
                {'id': 'server_3', 'cost_rub': 1500000,
                 'latency_ms': 2, 'failure_rate': 0.0001},
            ]
            placement = optimize_placement(
                components, nodes,
                {'max_latency': 100.0, 'max_cost': 10000000},
            )
            result.optimized_config = placement
            timings['step4_optimization'] = time.time() - t0
            if verbose:
                logger.info(f"  ✅ {timings['step4_optimization']:.2f}с | "
                           f"решений: {placement['n_solutions']}")
        except Exception as e:
            result.errors.append(f"Шаг 4: {e}")
            logger.exception(f"  ❌ {e}")
            return result
        
        # Шаг 5
        if verbose:
            logger.info("Шаг 5/6: Симуляция качества")
        t0 = time.time()
        try:
            sim_comps = [
                {'id': c['id'], 'capacity': c.get('capacity', 5),
                 'processing_time': c.get('latency', 10) / 1000.0}
                for c in best_arch['components']
            ]
            quality = evaluate_architecture({'components': sim_comps})
            result.quality_assessment = quality
            timings['step5_simulation'] = time.time() - t0
            if verbose:
                logger.info(f"  ✅ {timings['step5_simulation']:.2f}с | "
                           f"score: {quality['overall_score']:.4f}")
        except Exception as e:
            result.errors.append(f"Шаг 5: {e}")
            logger.exception(f"  ❌ {e}")
        
        # Шаг 6
        if verbose:
            logger.info("Шаг 6/6: Интерпретация")
        t0 = time.time()
        try:
            features = self.classifier.extract_features(
                result.requirements.get('entities', []), context,
            )
            result.explanation = self.explainer.explain(features, top_k=10)
            timings['step6_xai'] = time.time() - t0
            if verbose:
                logger.info(f"  ✅ {timings['step6_xai']:.2f}с")
        except Exception as e:
            result.errors.append(f"Шаг 6: {e}")
            logger.exception(f"  ❌ {e}")
        
        timings['total'] = time.time() - total_start
        result.timings = timings
        
        if verbose:
            logger.info("=" * 60)
            logger.info(f"✅ Конвейер завершён за {timings['total']:.2f}с")
            logger.info("=" * 60)
        
        return result

