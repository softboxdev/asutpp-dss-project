"""Компонентная модель архитектуры."""
from typing import Dict, List
from .base import ReportSection


class ComponentModelBuilder(ReportSection):
    """Спецификация компонентов."""
    
    name = "component_model"
    title = "Компонентная модель"
    order = 20
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        """Построить спецификацию."""
        if not pipeline_result.architectures:
            return {'error': 'no_architectures'}
        
        arch = pipeline_result.architectures[0]
        components = arch.get('components', [])
        
        return {
            'pattern': arch.get('pattern'),
            'total_components': len(components),
            'components': [
                self._specify_component(c, context)
                for c in components
            ],
            'dependency_matrix': self._build_dependency_matrix(components),
        }
    
    def _specify_component(self, comp: Dict, context: Dict) -> Dict:
        """Спецификация одного компонента."""
        ctype = comp.get('type', 'unknown')
        
        # Шаблоны характеристик по типу
        templates = {
            'sensor_adapter': {
                'responsibilities': [
                    'Сбор данных с датчиков',
                    'Нормализация сигналов',
                    'Валидация диапазонов',
                ],
                'interfaces': ['Modbus TCP', 'OPC UA', 'Profinet'],
                'technologies': ['Python', 'asyncua', 'pymodbus'],
            },
            'controller': {
                'responsibilities': [
                    'PID-регулирование',
                    'Аварийная остановка',
                    'Логика блокировок',
                ],
                'interfaces': ['IEC 61131-3', 'OPC UA'],
                'technologies': ['Python', 'pycomm3', 'asyncua'],
            },
            'historian': {
                'responsibilities': [
                    'Хранение временных рядов',
                    'Агрегация данных',
                    'Retention policy',
                ],
                'interfaces': ['REST API', 'SQL', 'OPC UA'],
                'technologies': ['TimescaleDB', 'PostgreSQL', 'Redis'],
            },
            'hmi': {
                'responsibilities': [
                    'Отображение данных',
                    'Управление оператором',
                    'Алармы',
                ],
                'interfaces': ['REST API', 'WebSocket'],
                'technologies': ['React', 'D3.js', 'WebSocket'],
            },
            'business_logic': {
                'responsibilities': [
                    'Бизнес-правила',
                    'Оркестрация',
                    'Уведомления',
                ],
                'interfaces': ['REST API', 'gRPC'],
                'technologies': ['Python', 'FastAPI'],
            },
            'event_bus': {
                'responsibilities': [
                    'Маршрутизация событий',
                    'Pub/Sub',
                    'Гарантия доставки',
                ],
                'interfaces': ['AMQP', 'MQTT'],
                'technologies': ['RabbitMQ', 'Kafka'],
            },
        }
        
        template = templates.get(ctype, {
            'responsibilities': ['Не указано'],
            'interfaces': ['Не указано'],
            'technologies': ['Не указано'],
        })
        
        return {
            'id': comp['id'],
            'type': ctype,
            'responsibilities': template['responsibilities'],
            'interfaces': template['interfaces'],
            'technologies': template['technologies'],
            'resources': {
                'cpu_cores': comp.get('capacity', 1),
                'ram_gb': 4,
                'disk_gb': 20,
            },
            'sla': {
                'uptime': '99.95%',
                'response_time_ms': comp.get('latency', 100),
            },
            'safety': {
                'sil_level': context.get('safety_level_sil', 0),
                'standards': ['IEC 61508'] if context.get('safety_level_sil', 0) > 0 else [],
            },
            'dependencies': [],
        }
    
    def _build_dependency_matrix(self, components: List[Dict]) -> Dict:
        """Матрица зависимостей."""
        comp_ids = [c['id'] for c in components]
        
        # Типичные зависимости
        deps = {
            'controller': ['sensor_adapter'],
            'historian': ['controller'],
            'hmi': ['controller', 'historian'],
            'business_logic': ['controller', 'historian'],
        }
        
        matrix = {}
        for comp_id in comp_ids:
            matrix[comp_id] = deps.get(comp_id, [])
        
        return matrix