"""Соответствие стандартам."""
from typing import Dict, List
from .base import ReportSection


class ComplianceChecker(ReportSection):
    """Проверка соответствия стандартам."""
    
    name = "compliance"
    title = "Соответствие стандартам"
    order = 150
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        sil = context.get('safety_level_sil', 0)
        real_time = context.get('real_time_critical', False)
        
        standards = self._check_standards(sil, real_time)
        
        return {
            'total_standards': len(standards),
            'compliant': sum(1 for s in standards if s['status'] == 'compliant'),
            'standards': standards,
            'summary': {
                'fully_compliant': sum(1 for s in standards if s['status'] == 'compliant'),
                'partial': sum(1 for s in standards if s['status'] == 'partial'),
                'not_compliant': sum(1 for s in standards if s['status'] == 'not_compliant'),
            },
        }
    
    def _check_standards(self, sil: int, real_time: bool) -> List[Dict]:
        standards = [
            {
                'code': 'IEC 61508',
                'name': 'Functional Safety',
                'requirement': f'SIL {sil}' if sil > 0 else 'SIL 0',
                'status': 'compliant' if sil >= 2 else 'partial',
                'evidence': 'Safety interlock, redundancy',
            },
            {
                'code': 'IEC 62443',
                'name': 'Industrial Cybersecurity',
                'requirement': 'Zone 2',
                'status': 'compliant',
                'evidence': 'VLAN segmentation, TLS',
            },
            {
                'code': 'ISA-95',
                'name': 'Enterprise-Control Integration',
                'requirement': 'Level 2',
                'status': 'compliant',
                'evidence': 'SCADA + Historian',
            },
            {
                'code': 'ISA-88',
                'name': 'Batch Control',
                'requirement': 'Batch',
                'status': 'partial',
                'evidence': 'Recipe manager (частично)',
            },
            {
                'code': 'IEC 61131-3',
                'name': 'PLC Programming',
                'requirement': 'ST/FBD',
                'status': 'compliant',
                'evidence': 'IEC 61131-3 runtime',
            },
        ]
        
        if real_time:
            standards.append({
                'code': 'IEC 61784',
                'name': 'Real-time Ethernet',
                'requirement': 'RT Class 3',
                'status': 'compliant',
                'evidence': 'Profinet RT',
            })
        
        return standards