"""VAE-генератор архитектур."""
import numpy as np
import networkx as nx
from typing import Dict, List
from loguru import logger


class ArchitectureVAE:
    def __init__(self):
        logger.info("ArchitectureVAE готов")
    
    def generate(self, pattern: Dict, context: Dict, n_samples: int = 10) -> List[Dict]:
        rng = np.random.RandomState(42)
        name = pattern.get('pattern', 'layered')
        
        architectures = []
        for i in range(n_samples):
            components = self._get_components(name, rng)
            architectures.append({
                'pattern': name,
                'components': components,
                'seed': i,
            })
        
        logger.info(f"Сгенерировано {len(architectures)} архитектур")
        return architectures
    
    def _get_components(self, pattern: str, rng: np.random.RandomState) -> List[Dict]:
        base = [
            {'id': 'sensor_adapter', 'type': 'sensor_adapter',
             'capacity': 10, 'cost': 50000, 'latency': 5},
            {'id': 'controller', 'type': 'controller',
             'capacity': 5, 'cost': 200000, 'latency': 10},
            {'id': 'historian', 'type': 'historian',
             'capacity': 20, 'cost': 300000, 'latency': 15},
            {'id': 'hmi', 'type': 'hmi',
             'capacity': 8, 'cost': 100000, 'latency': 20},
        ]
        
        if pattern == 'event_driven':
            base.append({'id': 'event_bus', 'type': 'event_bus',
                         'capacity': 25, 'cost': 250000, 'latency': 5})
        elif pattern == 'layered':
            base.append({'id': 'business_logic', 'type': 'business_logic',
                         'capacity': 10, 'cost': 180000, 'latency': 10})
        
        return base
    
    def to_graph(self, architecture: Dict) -> nx.DiGraph:
        G = nx.DiGraph()
        for comp in architecture['components']:
            G.add_node(comp['id'], **comp)
        
        comps = architecture['components']
        for i in range(len(comps) - 1):
            G.add_edge(comps[i]['id'], comps[i+1]['id'], type='data_flow')
        
        return G
