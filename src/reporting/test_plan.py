"""План тестирования."""
from typing import Dict, List
from .base import ReportSection


class TestPlanBuilder(ReportSection):
    """План тестирования."""
    
    name = "test_plan"
    title = "План тестирования"
    order = 160
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        test_types = self._build_test_types(pipeline_result)
        
        return {
            'total_tests': sum(t['count'] for t in test_types),
            'test_types': test_types,
            'coverage_target': 80,
            'tools': self._tools(),
        }
    
    def _build_test_types(self, pipeline_result) -> List[Dict]:
        return [
            {
                'type': 'Unit',
                'count': 150,
                'tool': 'pytest',
                'coverage': 'functions',
                'duration_days': 10,
            },
            {
                'type': 'Integration',
                'count': 40,
                'tool': 'pytest + httpx',
                'coverage': 'API',
                'duration_days': 10,
            },
            {
                'type': 'E2E',
                'count': 20,
                'tool': 'Playwright',
                'coverage': 'user scenarios',
                'duration_days': 5,
            },
            {
                'type': 'Load',
                'count': 5,
                'tool': 'Locust',
                'coverage': '1000 RPS',
                'duration_days': 3,
            },
            {
                'type': 'Security',
                'count': 10,
                'tool': 'OWASP ZAP',
                'coverage': 'OWASP Top 10',
                'duration_days': 2,
            },
        ]
    
    def _tools(self) -> Dict:
        return {
            'unit': 'pytest',
            'api': 'pytest + httpx',
            'e2e': 'Playwright',
            'load': 'Locust',
            'security': 'OWASP ZAP',
            'coverage': 'coverage.py',
        }