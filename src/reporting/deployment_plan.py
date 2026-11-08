"""План развёртывания."""
from typing import Dict, List
from .base import ReportSection


class DeploymentPlanner(ReportSection):
    """План развёртывания."""
    
    name = "deployment"
    title = "План развёртывания"
    order = 170
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        team = context.get('team_size', 5)
        
        return {
            'environments': self._environments(),
            'rollout_phases': self._rollout_phases(),
            'infrastructure': self._infrastructure(),
            'mermaid': self._to_mermaid(),
        }
    
    def _environments(self) -> List[Dict]:
        return [
            {
                'name': 'Development',
                'config': 'Docker Compose',
                'servers': 1,
                'purpose': 'Разработка и отладка',
                'data': 'synthetic',
            },
            {
                'name': 'Staging',
                'config': 'Kubernetes (3 nodes)',
                'servers': 3,
                'purpose': 'Тестирование',
                'data': 'anonymized production',
            },
            {
                'name': 'Production',
                'config': 'Kubernetes (6+ nodes)',
                'servers': 6,
                'purpose': 'Промышленная эксплуатация',
                'data': 'real',
            },
        ]
    
    def _rollout_phases(self) -> List[Dict]:
        return [
            {
                'phase': 1,
                'duration_weeks': 2,
                'components': ['sensor_adapter', 'controller'],
                'risk': 'low',
            },
            {
                'phase': 2,
                'duration_weeks': 3,
                'components': ['historian', 'hmi'],
                'risk': 'medium',
            },
            {
                'phase': 3,
                'duration_weeks': 2,
                'components': ['business_logic', 'integrations'],
                'risk': 'medium',
            },
        ]
    
    def _infrastructure(self) -> Dict:
        return {
            'compute': {
                'dev': '1 server (8 cores, 32 GB RAM)',
                'staging': '3 servers (16 cores, 64 GB RAM)',
                'prod': '6 servers (32 cores, 128 GB RAM)',
            },
            'network': {
                'dev': '1 Gbps',
                'staging': '1 Gbps',
                'prod': '10 Gbps + redundancy',
            },
            'storage': {
                'dev': '500 GB SSD',
                'staging': '2 TB SSD',
                'prod': '10 TB SSD (RAID 10)',
            },
        }
    
    def _to_mermaid(self) -> str:
        return """graph TD
    subgraph DEV["Development"]
        D1[Docker Compose]
        D2[1 Server]
    end
    
    subgraph STAGING["Staging"]
        S1[K8s 3 nodes]
        S2[2 replicas]
    end
    
    subgraph PROD["Production"]
        P1[K8s 6+ nodes]
        P2[3 replicas]
        P3[Backup daily]
    end
    
    DEV -->|CI/CD| STAGING
    STAGING -->|manual approve| PROD"""