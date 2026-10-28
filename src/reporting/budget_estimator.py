"""Оценка бюджета."""
from typing import Dict
from .base import ReportSection


class BudgetEstimator(ReportSection):
    """Бюджет проекта."""
    
    name = "budget"
    title = "Бюджет"
    order = 110
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        # Базовая стоимость из effort
        from .effort_estimator import EffortEstimator
        effort = EffortEstimator(self.output_dir).build(pipeline_result, context)
        
        labor_cost = effort['total_cost_rub']
        
        # Оборудование
        equipment = self._equipment_cost(context)
        
        # Лицензии
        licenses = self._license_cost()
        
        # Обучение
        training = self._training_cost(context)
        
        # Резерв 20%
        subtotal = labor_cost + equipment + licenses + training
        reserve = int(subtotal * 0.2)
        total = subtotal + reserve
        
        return {
            'labor_cost_rub': labor_cost,
            'equipment_rub': equipment,
            'licenses_rub': licenses,
            'training_rub': training,
            'subtotal_rub': subtotal,
            'reserve_rub': reserve,
            'total_rub': total,
            'breakdown': {
                'labor_percent': round(labor_cost / total * 100, 1),
                'equipment_percent': round(equipment / total * 100, 1),
                'licenses_percent': round(licenses / total * 100, 1),
                'training_percent': round(training / total * 100, 1),
                'reserve_percent': round(reserve / total * 100, 1),
            },
        }
    
    def _equipment_cost(self, context: Dict) -> int:
        servers = 4  # из load_calculator
        cost_per_server = 300_000  # сервер
        network = 200_000  # сеть
        plc = 500_000  # ПЛК
        return servers * cost_per_server + network + plc
    
    def _license_cost(self) -> int:
        return 0  # всё open-source
    
    def _training_cost(self, context: Dict) -> int:
        team = context.get('team_size', 5)
        return team * 3 * 8 * 5000  # 3 дня × 8 ч × 5000 ₽/ч