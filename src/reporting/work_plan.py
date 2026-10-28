"""План работ."""
from typing import Dict, List
from .base import ReportSection


class WorkPlanBuilder(ReportSection):
    """План работ с Gantt-диаграммой."""
    
    name = "work_plan"
    title = "План работ"
    order = 80
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        pattern = pipeline_result.patterns[0]['pattern'] if pipeline_result.patterns else 'layered'
        team = context.get('team_size', 5)
        timeline = context.get('timeline_months', 6)
        
        phases = self._build_phases(pattern, team)
        gantt = self._build_gantt(phases)
        
        return {
            'pattern': pattern,
            'total_days': sum(p['duration_days'] for p in phases),
            'phases': phases,
            'gantt_mermaid': gantt,
            'critical_path': self._critical_path(phases),
        }
    
    def _build_phases(self, pattern: str, team: int) -> List[Dict]:
        base_phases = [
            {
                'name': 'Анализ',
                'description': 'Анализ требований, интервью, онтология',
                'duration_days': 10,
                'roles': ['Архитектор', 'PM'],
                'deliverables': ['Требования v1.0'],
            },
            {
                'name': 'Проектирование',
                'description': 'Выбор паттернов, компонентная модель, диаграммы',
                'duration_days': 15,
                'roles': ['Архитектор', 'Senior Dev'],
                'deliverables': ['Архитектурная модель'],
            },
            {
                'name': 'Backend',
                'description': 'DACIE, классификатор, VAE, оптимизатор, API',
                'duration_days': 30,
                'roles': ['ML Engineer', 'Backend Dev'],
                'deliverables': ['API v1.0'],
            },
            {
                'name': 'Frontend',
                'description': 'UI, интеграция с API, визуализация',
                'duration_days': 25,
                'roles': ['Frontend Dev', 'Designer'],
                'deliverables': ['UI v1.0'],
            },
            {
                'name': 'Интеграция',
                'description': 'OPC UA, Modbus, SCADA, MES',
                'duration_days': 10,
                'roles': ['Integration Eng.'],
                'deliverables': ['Integration v1.0'],
            },
            {
                'name': 'Тестирование',
                'description': 'Unit, integration, E2E, load',
                'duration_days': 15,
                'roles': ['QA'],
                'deliverables': ['RC v1.0'],
            },
            {
                'name': 'Документация',
                'description': 'Техническая, пользовательская, API',
                'duration_days': 10,
                'roles': ['Техписатель'],
                'deliverables': ['Документация'],
            },
            {
                'name': 'Внедрение',
                'description': 'Пилот, обучение, production',
                'duration_days': 15,
                'roles': ['DevOps', 'PM'],
                'deliverables': ['Production v1.0'],
            },
        ]
        
        # Параллельные работы для больших команд
        if team >= 8:
            base_phases[2]['duration_days'] = int(base_phases[2]['duration_days'] * 0.7)
            base_phases[3]['duration_days'] = int(base_phases[3]['duration_days'] * 0.7)
        
        return base_phases
    
    def _build_gantt(self, phases: List[Dict]) -> str:
        lines = [
            "gantt",
            "    title План работ по проекту",
            "    dateFormat YYYY-MM-DD",
            "    axisFormat %b %Y",
            "",
        ]
        
        from datetime import datetime, timedelta
        current = datetime(2025, 11, 1)
        
        for i, phase in enumerate(phases):
            start = current.strftime("%Y-%m-%d")
            end = (current + timedelta(days=phase['duration_days'])).strftime("%Y-%m-%d")
            section = f"    section {phase['name']}"
            task = f"    {phase['name']} :{chr(97+i)}1, {start}, {phase['duration_days']}d"
            lines.append(section)
            lines.append(task)
            lines.append("")
            current += timedelta(days=phase['duration_days'])
        
        return '\n'.join(lines)
    
    def _critical_path(self, phases: List[Dict]) -> List[str]:
        """Критический путь."""
        return [p['name'] for p in phases]