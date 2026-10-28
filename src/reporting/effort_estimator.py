"""Оценка трудозатрат."""
from typing import Dict, List
from .base import ReportSection


class EffortEstimator(ReportSection):
    """Оценка часов и стоимости."""
    
    name = "effort"
    title = "Оценка трудозатрат"
    order = 90
    
    # Ставки (₽/час)
    RATES = {
        'Архитектор': 3000,
        'Senior Dev': 2500,
        'ML Engineer': 2500,
        'Backend Dev': 2000,
        'Frontend Dev': 2000,
        'Integration Eng.': 2500,
        'QA': 1500,
        'DevOps': 2500,
        'PM': 2500,
        'Техписатель': 1500,
        'Designer': 2000,
    }
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        team = context.get('team_size', 5)
        pattern = pipeline_result.patterns[0]['pattern'] if pipeline_result.patterns else 'layered'
        
        phases = self._estimate_phases(pattern, team)
        total_hours = sum(p['hours'] for p in phases)
        
        by_role = self._compute_by_role(phases)
        total_cost = sum(r['cost'] for r in by_role.values())
        
        return {
            'total_hours': total_hours,
            'total_calendar_days': total_hours / 8,
            'total_person_months': round(total_hours / (8 * 22), 1),
            'total_cost_rub': total_cost,
            'by_phase': phases,
            'by_role': by_role,
            'comparison': self._compare_with_traditional(total_hours),
        }
    
    def _estimate_phases(self, pattern: str, team: int) -> List[Dict]:
        base = [
            {'name': 'Анализ', 'hours': 80, 'roles': {'Архитектор': 40, 'PM': 20, 'Техписатель': 20}},
            {'name': 'Проектирование', 'hours': 120, 'roles': {'Архитектор': 60, 'Senior Dev': 60}},
            {'name': 'Backend', 'hours': 320, 'roles': {'ML Engineer': 240, 'Backend Dev': 80}},
            {'name': 'Frontend', 'hours': 200, 'roles': {'Frontend Dev': 150, 'Designer': 50}},
            {'name': 'Интеграция', 'hours': 120, 'roles': {'Integration Eng.': 120}},
            {'name': 'Тестирование', 'hours': 160, 'roles': {'QA': 160}},
            {'name': 'Документация', 'hours': 80, 'roles': {'Техписатель': 60, 'Backend Dev': 20}},
            {'name': 'Внедрение', 'hours': 80, 'roles': {'DevOps': 40, 'PM': 40}},
        ]
        
        # Корректировка для больших команд
        if team >= 8:
            for phase in base:
                if phase['name'] in ['Backend', 'Frontend']:
                    phase['hours'] = int(phase['hours'] * 0.85)
        
        return base
    
    def _compute_by_role(self, phases: List[Dict]) -> Dict:
        by_role = {}
        for phase in phases:
            for role, hours in phase['roles'].items():
                if role not in by_role:
                    by_role[role] = {'hours': 0, 'rate': self.RATES.get(role, 2000), 'cost': 0}
                by_role[role]['hours'] += hours
                by_role[role]['cost'] = by_role[role]['hours'] * by_role[role]['rate']
        
        return by_role
    
    def _compare_with_traditional(self, total: int) -> Dict:
        traditional = 2500  # традиционная АСУ ТП без автоматизации
        return {
            'traditional_hours': traditional,
            'our_hours': total,
            'savings_hours': traditional - total,
            'savings_percent': round((traditional - total) / traditional * 100, 1),
        }