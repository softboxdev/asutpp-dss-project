"""Матрица трассируемости."""
from typing import Dict, List
from .base import ReportSection


class TraceabilityBuilder(ReportSection):
    """Трассировка требований → компоненты → тесты."""
    
    name = "traceability"
    title = "Матрица трассируемости"
    order = 140
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        entities = pipeline_result.requirements.get('entities', [])
        
        # Формируем матрицу
        matrix = []
        for i, entity in enumerate(entities[:20]):
            req_id = f"REQ-{i+1:03d}"
            matrix.append({
                'requirement_id': req_id,
                'requirement_text': entity.get('text', '')[:50],
                'requirement_type': entity.get('type', ''),
                'component': self._map_to_component(entity),
                'test_id': f"T-{i+1:03d}",
                'test_status': 'planned',
                'doc_section': self._map_to_doc(entity),
            })
        
        # Покрытие
        coverage = {
            'total_requirements': len(matrix),
            'covered_by_components': sum(1 for m in matrix if m['component']),
            'covered_by_tests': sum(1 for m in matrix if m['test_id']),
            'coverage_percent': round(
                sum(1 for m in matrix if m['component']) / max(len(matrix), 1) * 100, 1
            ),
        }
        
        return {
            'matrix': matrix,
            'coverage': coverage,
        }
    
    def _map_to_component(self, entity: Dict) -> str:
        """Маппинг требования на компонент."""
        etype = entity.get('type', '')
        mapping = {
            'sensor': 'sensor_adapter',
            'controller': 'controller',
            'requirement_functional': 'business_logic',
            'requirement_safety': 'controller',
            'requirement_performance': 'business_logic',
            'requirement_reliability': 'historian',
            'interface': 'integration_layer',
        }
        return mapping.get(etype, '')
    
    def _map_to_doc(self, entity: Dict) -> str:
        """Маппинг на раздел документации."""
        etype = entity.get('type', '')
        mapping = {
            'sensor': 'SPEC-001',
            'controller': 'SPEC-002',
            'requirement_safety': 'SAFETY-001',
            'interface': 'INT-001',
        }
        return mapping.get(etype, 'GENERAL')