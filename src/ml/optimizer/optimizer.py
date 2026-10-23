"""Оптимизатор топологии и размещения."""
import numpy as np
import networkx as nx
from typing import Dict, List
from loguru import logger


class TopologyOptimizer:
    def __init__(self):
        logger.info("TopologyOptimizer готов")
    
    def optimize(
        self,
        initial_graph: nx.DiGraph,
        requirements: Dict,
        num_iterations: int = 20,
    ) -> nx.DiGraph:
        optimized = initial_graph.copy()
        
        if optimized.number_of_nodes() > 1:
            if not nx.is_weakly_connected(optimized):
                nodes = list(optimized.nodes())
                for i in range(len(nodes) - 1):
                    if not optimized.has_edge(nodes[i], nodes[i+1]):
                        optimized.add_edge(nodes[i], nodes[i+1], type='optimized')
        
        logger.info(
            f"Оптимизация: {optimized.number_of_nodes()} узлов, "
            f"{optimized.number_of_edges()} рёбер"
        )
        return optimized


def optimize_placement(
    components: List[Dict],
    nodes: List[Dict],
    constraints: Dict,
    pop_size: int = 50,
    n_gen: int = 20,
) -> Dict:
    logger.info(f"Размещение: {len(components)} × {len(nodes)}")
    
    rng = np.random.RandomState(42)
    pareto = []
    
    for _ in range(10):
        placement = [int(rng.randint(0, len(nodes))) for _ in components]
        
        latency = np.mean([
            comp.get('latency', 10) + nodes[p].get('latency_ms', 5)
            for comp, p in zip(components, placement)
        ])
        
        used = set(placement)
        cost = sum(nodes[i].get('cost_rub', 500000) for i in used)
        
        failure_prob = 1.0
        for i in used:
            failure_prob *= (1 - nodes[i].get('failure_rate', 0.001))
        
        pareto.append({
            'placement': placement,
            'latency': float(latency),
            'cost': float(cost),
            'unreliability': float(failure_prob),
        })
    
    pareto.sort(
        key=lambda x: 0.4 * x['latency'] / 100
                    + 0.3 * x['cost'] / 1e6
                    + 0.3 * x['unreliability']
    )
    
    return {
        'pareto_front': pareto,
        'best': pareto[0] if pareto else None,
        'n_solutions': len(pareto),
    }
