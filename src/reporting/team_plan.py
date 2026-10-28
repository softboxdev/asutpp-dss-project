"""План команды."""
from typing import Dict, List
from .base import ReportSection


class TeamPlanner(ReportSection):
    """Планирование команды."""
    
    name = "team"
    title = "Команда"
    order = 120
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        # Из effort
        from .effort_estimator import EffortEstimator
        effort = EffortEstimator(self.output_dir).build(pipeline_result, context)
        
        by_role = effort['by_role']
        total_hours = effort['total_hours']
        
        # Определяем FTE
        team = []
        total_fte = 0
        
        for role, data in by_role.items():
            fte = round(data['hours'] / total_hours, 2)
            team.append({
                'role': role,
                'hours': data['hours'],
                'fte': fte,
                'rate_rub': data['rate'],
                'cost_rub': data['cost'],
            })
            total_fte += fte
        
        return {
            'total_roles': len(team),
            'total_fte': round(total_fte, 2),
            'team': sorted(team, key=lambda x: x['hours'], reverse=True),
        }