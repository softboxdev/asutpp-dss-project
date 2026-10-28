"""SLA и метрики."""
from typing import Dict, List
from .base import ReportSection


class SLAMetricsBuilder(ReportSection):
    """SLA и ключевые метрики."""
    
    name = "sla"
    title = "SLA и метрики"
    order = 180
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        return {
            'sla': self._sla(),
            'metrics': self._metrics(),
            'monitoring': self._monitoring(),
            'alerting': self._alerting(),
        }
    
    def _sla(self) -> Dict:
        return {
            'availability': '99.95%',
            'response_time_p95_ms': 100,
            'response_time_p99_ms': 200,
            'throughput_rps': 1000,
            'mttr_hours': 1,
            'mtbf_hours': 10000,
            'rto_hours': 4,
            'rpo_hours': 1,
        }
    
    def _metrics(self) -> List[Dict]:
        return [
            {
                'name': 'Uptime',
                'target': '99.95%',
                'measurement': 'Prometheus uptime',
                'alert_threshold': '<99.9%',
            },
            {
                'name': 'Response time (p95)',
                'target': '<100ms',
                'measurement': 'APM',
                'alert_threshold': '>150ms',
            },
            {
                'name': 'Throughput',
                'target': '>1000 RPS',
                'measurement': 'Load balancer',
                'alert_threshold': '<800 RPS',
            },
            {
                'name': 'Error rate',
                'target': '<0.1%',
                'measurement': 'APM',
                'alert_threshold': '>0.5%',
            },
            {
                'name': 'CPU utilization',
                'target': '<70%',
                'measurement': 'Prometheus',
                'alert_threshold': '>85%',
            },
            {
                'name': 'Memory utilization',
                'target': '<80%',
                'measurement': 'Prometheus',
                'alert_threshold': '>90%',
            },
        ]
    
    def _monitoring(self) -> Dict:
        return {
            'metrics': 'Prometheus',
            'dashboards': 'Grafana',
            'logs': 'Loki / ELK',
            'traces': 'Jaeger',
            'apm': 'OpenTelemetry',
        }
    
    def _alerting(self) -> List[Dict]:
        return [
            {'severity': 'critical', 'channel': 'PagerDuty + SMS', 'response': '15 min'},
            {'severity': 'high', 'channel': 'Slack + Email', 'response': '1 hour'},
            {'severity': 'medium', 'channel': 'Slack', 'response': '4 hours'},
            {'severity': 'low', 'channel': 'Email', 'response': '1 day'},
        ]