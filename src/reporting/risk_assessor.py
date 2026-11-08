"""Оценка рисков."""
from typing import Dict, List
from .base import ReportSection


class RiskAssessor(ReportSection):
    """Риски и митигация."""
    
    name = "risks"
    title = "Риски"
    order = 130
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        risks = self._identify_risks(pipeline_result, context)
        
        return {
            'total_risks': len(risks),
            'critical_count': sum(1 for r in risks if r['impact'] == 'critical'),
            'risks': risks,
            'risk_matrix': self._build_matrix(risks),
        }
    
    def _identify_risks(self, pipeline_result, context: Dict) -> List[Dict]:
        sil = context.get('safety_level_sil', 0)
        real_time = context.get('real_time_critical', False)
        
        risks = [
            {
                'id': 'R-001',
                'name': 'Задержка поставки оборудования',
                'category': 'supply',
                'probability': 'medium',
                'impact': 'high',
                'description': 'Оборудование может быть поставлено позже запланированного',
                'mitigation': 'Буфер 2 недели в плане, альтернативные поставщики',
                'owner': 'PM',
            },
            {
                'id': 'R-002',
                'name': 'Ошибки AI на критических данных',
                'category': 'technical',
                'probability': 'high' if pipeline_result.patterns else 'medium',
                'impact': 'critical',
                'description': 'LLM может ошибиться при извлечении критических требований',
                'mitigation': 'Символьная верификация, ручная проверка SIL-требований',
                'owner': 'ML Engineer',
            },
            {
                'id': 'R-003',
                'name': 'Несовместимость с SCADA',
                'category': 'technical',
                'probability': 'medium',
                'impact': 'high',
                'description': 'OPC UA может не поддерживаться старой SCADA',
                'mitigation': 'Прототип интеграции в Sprint 3',
                'owner': 'Integration Eng.',
            },
            {
                'id': 'R-004',
                'name': 'Нехватка компетенций',
                'category': 'team',
                'probability': 'low',
                'impact': 'high',
                'description': 'Команда может не иметь опыта в ML/АСУ ТП',
                'mitigation': 'Обучение, консультанты',
                'owner': 'PM',
            },
            {
                'id': 'R-005',
                'name': 'Изменение требований',
                'category': 'requirements',
                'probability': 'high',
                'impact': 'medium',
                'description': 'Заказчик может изменить требования',
                'mitigation': 'Agile-подход, спринты по 2 недели',
                'owner': 'PM',
            },
            {
                'id': 'R-006',
                'name': 'OOM на GPU',
                'category': 'technical',
                'probability': 'medium',
                'impact': 'medium',
                'description': 'Модель может не поместиться в VRAM',
                'mitigation': 'Квантизация, fallback на CPU, модель 1.5B',
                'owner': 'ML Engineer',
            },
        ]
        
        # Добавляем SIL-риск если нужно
        if sil >= 2:
            risks.append({
                'id': 'R-007',
                'name': 'Несоответствие SIL 2',
                'category': 'compliance',
                'probability': 'low',
                'impact': 'critical',
                'description': 'Система может не пройти сертификацию SIL 2',
                'mitigation': 'Аудит в Sprint 4, привлечение сертификатора',
                'owner': 'Архитектор',
            })
        
        return risks
    
    def _build_matrix(self, risks: List[Dict]) -> Dict:
        """Матрица рисков."""
        matrix = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
        }
        
        for risk in risks:
            matrix[risk['impact']].append(risk['id'])
        
        return matrix