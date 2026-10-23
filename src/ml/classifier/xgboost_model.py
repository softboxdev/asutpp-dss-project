"""Классификатор архитектурных паттернов."""
import numpy as np
from typing import Dict, List
from loguru import logger


PATTERNS = [
    'monolithic', 'layered', 'event_driven', 'microservices',
    'pipe_filter', 'client_server', 'broker', 'cqrs',
    'hexagonal', 'soa', 'microkernel', 'blackboard',
]


class PatternClassifier:
    def __init__(self):
        logger.info("PatternClassifier готов")
    
    def extract_features(self, entities: List[Dict], context: Dict) -> np.ndarray:
        features = np.zeros(256)
        features[0] = len(entities)
        for e in entities:
            t = e.get('type', '')
            if 'functional' in t:
                features[1] += 1
            elif 'safety' in t:
                features[2] += 1
            elif 'performance' in t:
                features[3] += 1
            elif 'reliability' in t:
                features[4] += 1
        
        features[64] = context.get('team_size', 5)
        features[65] = context.get('budget_million_rub', 10)
        features[66] = context.get('timeline_months', 6)
        features[67] = float(context.get('real_time_critical', False))
        features[68] = context.get('safety_level_sil', 0)
        
        features[128] = context.get('num_external_systems', 0)
        features[129] = float(context.get('has_scada_integration', False))
        features[130] = float(context.get('has_mes_integration', False))
        
        return features
    
    def classify(self, entities: List[Dict], context: Dict) -> List[Dict]:
        features = self.extract_features(entities, context)
        
        real_time = context.get('real_time_critical', False)
        sil = context.get('safety_level_sil', 0)
        team = context.get('team_size', 5)
        ext = context.get('num_external_systems', 0)
        
        scores = {
            'layered': 0.7 + 0.1 * sil,
            'event_driven': 0.85 if real_time else 0.5,
            'microservices': 0.75 if (team > 10 and ext > 3) else 0.4,
            'monolithic': 0.7 if team < 5 else 0.3,
            'cqrs': 0.55,
            'pipe_filter': 0.6,
            'soa': 0.5,
            'hexagonal': 0.5,
        }
        
        total = sum(scores.values())
        sorted_patterns = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        return [
            {
                'pattern': p,
                'confidence': s / total if total > 0 else 0,
                'features': features,
            }
            for p, s in sorted_patterns[:5]
        ]
