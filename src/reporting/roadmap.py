"""Дорожная карта."""
from typing import Dict, List
from .base import ReportSection


class RoadmapBuilder(ReportSection):
    """Дорожная карта с milestones."""
    
    name = "roadmap"
    title = "Дорожная карта"
    order = 100
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        timeline = context.get('timeline_months', 6)
        
        milestones = self._build_milestones(timeline)
        
        return {
            'total_months': timeline,
            'milestones': milestones,
            'timeline_mermaid': self._build_mermaid(milestones),
        }
    
    def _build_milestones(self, timeline: int) -> List[Dict]:
        return [
            {
                'name': 'MVP',
                'month': 1,
                'criteria': [
                    'DACIE работает на тестовых данных',
                    'Классификатор выдаёт паттерны',
                    'VAE генерирует архитектуры',
                    'CLI-интерфейс',
                ],
                'deliverables': ['Работающий прототип'],
            },
            {
                'name': 'Alpha',
                'month': 3,
                'criteria': [
                    'Полный API (FastAPI)',
                    'UI (React) с визуализацией',
                    'Интеграция с OPC UA',
                    'Тесты: 70% coverage',
                ],
                'deliverables': ['Backend + Frontend'],
            },
            {
                'name': 'Beta',
                'month': 5,
                'criteria': [
                    'E2E-тесты пройдены',
                    'Нагрузочные тесты',
                    'Документация готова',
                    'Безопасность проверена',
                ],
                'deliverables': ['Тестирование завершено'],
            },
            {
                'name': 'Release',
                'month': timeline,
                'criteria': [
                    'Пилот на реальном объекте',
                    'Обучение персонала',
                    'SLA подтверждён',
                ],
                'deliverables': ['Production'],
            },
        ]
    
    def _build_mermaid(self, milestones: List[Dict]) -> str:
        lines = [
            "gantt",
            "    title Дорожная карта",
            "    dateFormat YYYY-MM-DD",
            "    axisFormat %b %Y",
            "",
        ]
        
        from datetime import datetime, timedelta
        current = datetime(2025, 11, 1)
        
        for i, m in enumerate(milestones):
            lines.append(f"    {m['name']} :milestone, m{i}, {current.strftime('%Y-%m-%d')}, 0d")
            current += timedelta(days=m['month'] * 30)
        
        return '\n'.join(lines)