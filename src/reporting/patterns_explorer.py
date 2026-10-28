"""Справочник архитектурных паттернов."""
from typing import Dict, List
from .base import ReportSection


class PatternsExplorer(ReportSection):
    """Объяснение архитектурных паттернов."""
    
    name = "patterns"
    title = "Архитектурные паттерны"
    order = 60
    
    def __init__(self, output_dir=None):
        super().__init__(output_dir)
        self.patterns = self._load_patterns()
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        pattern_names = [p['pattern'] for p in pipeline_result.patterns]
        
        return {
            'recommended': pattern_names,
            'details': {
                name: self.patterns.get(name, {})
                for name in pattern_names
            },
            'comparison': self._compare_patterns(pattern_names),
            'recommendations': self._recommend_for_context(context),
        }
    
    def _load_patterns(self) -> Dict:
        return {
            'layered': {
                'name': 'Слоистая архитектура (Layered)',
                'category': 'structural',
                'description': 'Организация системы в виде иерархии слоёв с четким разделением ответственности',
                'when_to_use': [
                    'Четкое разделение ответственности',
                    'Простота тестирования каждого слоя',
                    'Небольшая команда (до 10 человек)',
                    'Традиционные АСУ ТП',
                ],
                'pros': ['Понятная структура', 'Легко тестировать', 'Изолированные изменения'],
                'cons': ['Overhead', 'Сложно масштабировать'],
                'asutp_specific': 'Часто используется для традиционных АСУ ТП со SCADA',
                'mermaid': 'graph TD\n    A[Presentation] --> B[Business Logic]\n    B --> C[Data Access]\n    C --> D[Database]',
            },
            'event_driven': {
                'name': 'Событийно-ориентированная (Event-Driven)',
                'category': 'behavioral',
                'description': 'Компоненты взаимодействуют через события (event bus)',
                'when_to_use': [
                    'Асинхронная обработка',
                    'Много компонентов',
                    'Real-time критические системы',
                    'Высокие требования к масштабируемости',
                ],
                'pros': ['Слабая связанность', 'Масштабируемость', 'Асинхронность'],
                'cons': ['Сложнее отладка', 'Требует event bus'],
                'asutp_specific': 'Идеально для real-time АСУ ТП',
                'mermaid': 'graph LR\n    A[Sensor] --> E[Event Bus]\n    B[Controller] --> E\n    E --> C[Historian]\n    E --> D[HMI]',
            },
            'microservices': {
                'name': 'Микросервисная архитектура',
                'category': 'structural',
                'description': 'Система как набор независимых сервисов',
                'when_to_use': [
                    'Большая команда (10+)',
                    'Много интеграций',
                    'Независимое развёртывание',
                    'Разные технологии',
                ],
                'pros': ['Независимое развёртывание', 'Технологическая гибкость', 'Масштабируемость'],
                'cons': ['Сложность', 'Network overhead', 'DevOps-нагрузка'],
                'asutp_specific': 'Для крупных распределенных АСУ ТП',
                'mermaid': 'graph TD\n    A[API Gateway] --> B[Sensor Service]\n    A --> C[Control Service]\n    A --> D[Historian Service]',
            },
            'cqrs': {
                'name': 'CQRS',
                'category': 'behavioral',
                'description': 'Разделение операций чтения и записи',
                'when_to_use': [
                    'Разные нагрузки на чтение/запись',
                    'Сложные запросы',
                    'Event sourcing',
                ],
                'pros': ['Оптимизация чтения', 'Масштабирование'],
                'cons': ['Сложность', 'Eventual consistency'],
                'asutp_specific': 'Для систем с интенсивным чтением исторических данных',
                'mermaid': 'graph LR\n    A[Write API] --> B[Write DB]\n    B --> C[Event Bus]\n    C --> D[Read DB]\n    E[Read API] --> D',
            },
            'pipe_filter': {
                'name': 'Pipe-Filter',
                'category': 'behavioral',
                'description': 'Обработка данных через последовательность фильтров',
                'when_to_use': [
                    'Обработка потоков данных',
                    'ETL-процессы',
                    'Обработка сигналов',
                ],
                'pros': ['Простота', 'Переиспользование фильтров'],
                'cons': ['Не для интерактивных систем'],
                'asutp_specific': 'Для обработки сигналов и подготовки данных',
                'mermaid': 'graph LR\n    A[Raw Data] --> B[Filter 1]\n    B --> C[Filter 2]\n    C --> D[Result]',
            },
        }
    
    def _compare_patterns(self, names: List[str]) -> Dict:
        return {
            'complexity': {
                n: len(self.patterns.get(n, {}).get('pros', [])) +
                   len(self.patterns.get(n, {}).get('cons', []))
                for n in names
            },
            'team_size': {
                'layered': '3-10',
                'event_driven': '5-15',
                'microservices': '10+',
                'cqrs': '8+',
                'pipe_filter': '2-5',
            },
        }
    
    def _recommend_for_context(self, context: Dict) -> List[Dict]:
        team = context.get('team_size', 5)
        real_time = context.get('real_time_critical', False)
        ext = context.get('num_external_systems', 0)
        
        recommendations = []
        
        if team < 5:
            recommendations.append({
                'pattern': 'layered',
                'reason': 'Малая команда, простота важнее гибкости',
                'confidence': 0.9,
            })
        
        if real_time:
            recommendations.append({
                'pattern': 'event_driven',
                'reason': 'Real-time требования',
                'confidence': 0.85,
            })
        
        if team >= 10 and ext > 3:
            recommendations.append({
                'pattern': 'microservices',
                'reason': 'Большая команда и много интеграций',
                'confidence': 0.8,
            })
        
        return sorted(recommendations, key=lambda x: x['confidence'], reverse=True)