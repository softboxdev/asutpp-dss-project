"""SHAP-интерпретатор (fallback без SHAP)."""
import numpy as np
from typing import Dict, List
from loguru import logger


FEATURE_NAMES = [
    'num_entities', 'num_functional', 'num_safety',
    'num_performance', 'num_reliability',
    *[f'req_aux_{i}' for i in range(59)],
    *[f'graph_{i}' for i in range(64)],
    'team_size', 'budget', 'timeline', 'real_time', 'sil_level',
    'external_systems', 'has_scada', 'has_mes', 'has_erp',
    *[f'ctx_{i}' for i in range(55)],
    *[f'qual_{i}' for i in range(64)],
]


class ArchitectureExplainer:
    def __init__(self, classifier=None):
        self.classifier = classifier
        logger.info("ArchitectureExplainer готов")
    
    def explain(self, features: np.ndarray, top_k: int = 10) -> Dict:
        indices = np.argsort(np.abs(features))[-top_k:][::-1]
        
        return {
            'top_features': [
                {
                    'name': FEATURE_NAMES[i] if i < len(FEATURE_NAMES) else f'f_{i}',
                    'index': int(i),
                    'value': float(features[i]),
                    'importance': abs(float(features[i])),
                    'impact': 'positive' if features[i] > 0 else 'negative',
                }
                for i in indices
            ],
            'method': 'fallback',
        }

