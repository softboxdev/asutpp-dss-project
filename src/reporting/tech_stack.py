"""Рекомендации технологического стека."""
from typing import Dict, List
from .base import ReportSection


class TechStackRecommender(ReportSection):
    """Рекомендует технологии для каждого слоя."""
    
    name = "tech_stack"
    title = "Технологический стек"
    order = 30
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        pattern = pipeline_result.patterns[0]['pattern'] if pipeline_result.patterns else 'layered'
        
        return {
            'pattern': pattern,
            'layers': self._recommend_layers(pattern, context),
            'total_license_cost_rub': self._compute_license_cost(),
            'alternatives': self._alternatives(),
        }
    
    def _recommend_layers(self, pattern: str, context: Dict) -> List[Dict]:
        real_time = context.get('real_time_critical', False)
        
        layers = [
            {
                'level': 'Field',
                'purpose': 'Сбор данных с оборудования',
                'technologies': ['Modbus TCP', 'Profinet', 'HART', 'OPC UA'],
                'primary': 'Modbus TCP',
                'alternatives': ['Profinet', 'OPC UA'],
                'justification': 'Стандарт для промышленных датчиков',
                'license': 'free',
                'cost_rub': 0,
            },
            {
                'level': 'Control',
                'purpose': 'Логика управления',
                'technologies': ['IEC 61131-3 (ST, FBD)', 'Python', 'C++'],
                'primary': 'IEC 61131-3' if real_time else 'Python',
                'alternatives': ['Python' if real_time else 'IEC 61131-3'],
                'justification': 'Стандарт ПЛК' if real_time else 'Скорость разработки',
                'license': 'free',
                'cost_rub': 0,
            },
            {
                'level': 'Server',
                'purpose': 'Backend-сервисы',
                'technologies': ['Python 3.12', 'FastAPI', 'PostgreSQL'],
                'primary': 'Python + FastAPI',
                'alternatives': ['Java Spring', '.NET Core'],
                'justification': 'Быстрая разработка, AI/ML экосистема',
                'license': 'Apache 2.0',
                'cost_rub': 0,
            },
            {
                'level': 'Data',
                'purpose': 'Хранение данных',
                'technologies': ['TimescaleDB', 'PostgreSQL', 'Redis', 'MinIO'],
                'primary': 'TimescaleDB',
                'alternatives': ['InfluxDB', 'PostgreSQL'],
                'justification': 'Оптимизирован для временных рядов',
                'license': 'Apache 2.0',
                'cost_rub': 0,
            },
            {
                'level': 'UI',
                'purpose': 'Пользовательский интерфейс',
                'technologies': ['React', 'TypeScript', 'Grafana', 'Streamlit'],
                'primary': 'React + TypeScript',
                'alternatives': ['Vue', 'Angular', 'Streamlit'],
                'justification': 'Стандарт для АСУ ТП',
                'license': 'MIT',
                'cost_rub': 0,
            },
            {
                'level': 'Integration',
                'purpose': 'Интеграция с корпоративными системами',
                'technologies': ['OPC UA', 'REST API', 'gRPC', 'MQTT'],
                'primary': 'OPC UA + REST',
                'alternatives': ['gRPC', 'MQTT'],
                'justification': 'Стандарт SCADA/MES',
                'license': 'free',
                'cost_rub': 0,
            },
            {
                'level': 'DevOps',
                'purpose': 'Развёртывание и мониторинг',
                'technologies': ['Docker', 'Kubernetes', 'GitLab CI', 'Prometheus', 'Grafana'],
                'primary': 'Docker + GitLab CI',
                'alternatives': ['Jenkins', 'GitHub Actions'],
                'justification': 'Современный стандарт',
                'license': 'Apache 2.0',
                'cost_rub': 0,
            },
        ]
        
        return layers
    
    def _compute_license_cost(self) -> int:
        """Стоимость лицензий."""
        return 0  # всё open-source
    
    def _alternatives(self) -> Dict:
        """Альтернативы."""
        return {
            'scada': {
                'options': ['Siemens WinCC', 'AVEVA', 'Ignition'],
                'cost': 'от $10,000',
            },
            'historian': {
                'options': ['TimescaleDB (free)', 'InfluxDB', 'PI System'],
                'cost': '$0 - $50,000',
            },
        }