"""Симулятор качества архитектуры."""
import numpy as np
from typing import Dict, List
from loguru import logger


class ASUTPSimulator:
    def __init__(self, configuration: Dict):
        self.config = configuration
        self.components = configuration.get('components', [])
    
    def run_scenario(self, scenario: str = 'normal', duration: float = 10.0,
                     base_load: float = 10.0) -> Dict:
        if scenario == 'normal':
            load = base_load
        elif scenario == 'peak':
            load = base_load * 2.5
        elif scenario == 'failure':
            load = base_load * 1.5
        else:
            load = base_load
        
        base_latency = 0.05
        overload = max(1.0, load / (len(self.components) * 2))
        mean_rt = base_latency * overload
        
        samples = np.random.lognormal(
            mean=np.log(mean_rt), sigma=0.3, size=200,
        )
        
        return {
            'count': len(samples),
            'mean_response_time': float(np.mean(samples)),
            'p50_response_time': float(np.percentile(samples, 50)),
            'p95_response_time': float(np.percentile(samples, 95)),
            'p99_response_time': float(np.percentile(samples, 99)),
            'max_response_time': float(np.max(samples)),
            'throughput': len(samples) / duration,
        }


def evaluate_architecture(configuration: Dict) -> Dict:
    sim = ASUTPSimulator(configuration)
    results = {}
    for scenario in ['normal', 'peak', 'failure']:
        results[scenario] = sim.run_scenario(scenario)
    
    return {
        'scenarios': results,
        'overall_score': compute_score(results),
    }


def compute_score(results: Dict) -> float:
    weights = {'normal': 0.3, 'peak': 0.4, 'failure': 0.3}
    score = 0.0
    for scenario, metrics in results.items():
        p95 = metrics.get('p95_response_time', 0.1)
        score += weights[scenario] * (1.0 / (1.0 + p95))
    return score
