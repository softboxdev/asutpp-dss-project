"""Расчёт нагрузки на систему."""
import math
from typing import Dict, List
from .base import ReportSection


class LoadCalculator(ReportSection):
    """Расчёт нагрузки, ресурсов, узких мест."""
    
    name = "load"
    title = "Расчёт нагрузки"
    order = 70
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        io_points = context.get('num_io_points', 500)
        control_loops = context.get('num_control_loops', 25)
        data_volume = context.get('data_volume_gb_per_day', 10)
        
        input_load = self._calculate_input_load(io_points, control_loops, data_volume)
        
        if pipeline_result.architectures:
            arch = pipeline_result.architectures[0]
            per_component = self._calculate_component_load(arch, input_load)
        else:
            per_component = []
        
        resources = self._calculate_resources(per_component)
        bottlenecks = self._find_bottlenecks(per_component)
        recommendations = self._generate_recommendations(
            per_component, bottlenecks, resources
        )
        
        return {
            'input_load': input_load,
            'per_component': per_component,
            'resources': resources,
            'bottlenecks': bottlenecks,
            'recommendations': recommendations,
        }
    
    def _calculate_input_load(
        self, io_points: int, control_loops: int, data_volume: float,
    ) -> Dict:
        poll_rate_hz = 10
        events_per_sec = io_points * poll_rate_hz
        control_actions_per_sec = control_loops
        bytes_per_signal = 16
        bytes_per_sec = events_per_sec * bytes_per_signal
        bandwidth_mbps = (bytes_per_sec * 8) / 1e6
        
        return {
            'io_points': io_points,
            'control_loops': control_loops,
            'poll_rate_hz': poll_rate_hz,
            'events_per_second': events_per_sec,
            'control_actions_per_second': control_actions_per_sec,
            'bytes_per_second': bytes_per_sec,
            'bandwidth_mbps': round(bandwidth_mbps, 2),
            'data_per_day_gb': round((bytes_per_sec * 86400) / 1e9, 2),
            'data_per_year_gb': round((bytes_per_sec * 86400 * 365) / 1e9, 2),
        }
    
    def _calculate_component_load(
        self, architecture: Dict, input_load: Dict,
    ) -> List[Dict]:
        components = architecture.get('components', [])
        events_per_sec = input_load['events_per_second']
        
        load_factors = {
            'sensor_adapter': 1.0,
            'controller': 0.1,
            'historian': 1.0,
            'hmi': 0.05,
            'business_logic': 0.2,
            'event_bus': 1.0,
        }
        
        result = []
        for comp in components:
            ctype = comp.get('type', 'unknown')
            factor = load_factors.get(ctype, 0.1)
            comp_events = events_per_sec * factor
            cpu_per_event = 0.001
            cpu_cores = (comp_events * cpu_per_event) / 100
            ram_mb = 256 + (comp_events / 100) * 10
            
            disk_gb_day = 0
            if ctype == 'historian':
                disk_gb_day = input_load['data_per_day_gb']
            
            result.append({
                'id': comp['id'],
                'type': ctype,
                'events_per_second': round(comp_events, 0),
                'cpu_cores_required': round(max(cpu_cores, 0.25), 2),
                'ram_mb': round(ram_mb, 0),
                'disk_gb_per_day': round(disk_gb_day, 2),
                'network_mbps': round((comp_events * 16 * 8) / 1e6, 2),
            })
        
        return result
    
    def _calculate_resources(self, per_component: List[Dict]) -> Dict:
        total_cpu = sum(c['cpu_cores_required'] for c in per_component)
        total_ram = sum(c['ram_mb'] for c in per_component)
        total_disk = sum(c['disk_gb_per_day'] for c in per_component)
        total_network = sum(c['network_mbps'] for c in per_component)
        
        return {
            'total': {
                'cpu_cores': round(total_cpu, 1),
                'ram_gb': round(total_ram / 1024, 1),
                'disk_gb_per_day': round(total_disk, 1),
                'disk_gb_per_year': round(total_disk * 365, 1),
                'network_mbps': round(total_network, 1),
            },
            'with_reserve': {
                'cpu_cores': round(total_cpu * 1.3, 1),
                'ram_gb': round(total_ram / 1024 * 1.3, 1),
                'disk_gb_per_day': round(total_disk * 1.3, 1),
                'disk_gb_per_year': round(total_disk * 365 * 1.3, 1),
                'network_mbps': round(total_network * 1.3, 1),
            },
            'recommended_servers': self._recommend_servers(
                total_cpu, total_ram, total_disk
            ),
        }
    
    def _recommend_servers(
        self, cpu: float, ram_mb: float, disk_gb: float,
    ) -> List[Dict]:
        ram_gb = ram_mb / 1024
        cpu_with_reserve = cpu * 1.3
        ram_with_reserve = ram_gb * 1.3
        
        servers = []
        
        if cpu_with_reserve > 0:
            n_app = max(1, math.ceil(cpu_with_reserve / 8))
            servers.append({
                'role': 'Application',
                'count': n_app,
                'spec': '8 cores, 32 GB RAM, 500 GB SSD',
                'reason': f'{cpu_with_reserve:.1f} cores, {ram_with_reserve:.1f} GB',
            })
        
        if disk_gb > 0:
            servers.append({
                'role': 'Historian',
                'count': 1,
                'spec': f'8 cores, 64 GB RAM, {max(2000, disk_gb * 30):.0f} GB SSD',
                'reason': f'{disk_gb * 365:.0f} GB/год',
            })
        
        servers.append({
            'role': 'SCADA/HMI',
            'count': 2,
            'spec': '4 cores, 16 GB RAM, 256 GB SSD',
            'reason': 'Резервированная пара',
        })
        
        servers.append({
            'role': 'Database Replica',
            'count': 1,
            'spec': '8 cores, 32 GB RAM, 2 TB SSD',
            'reason': 'Отказоустойчивость',
        })
        
        return servers
    
    def _find_bottlenecks(self, per_component: List[Dict]) -> List[Dict]:
        bottlenecks = []
        
        for comp in per_component:
            issues = []
            if comp['events_per_second'] > 5000:
                issues.append('Высокая нагрузка событий')
            if comp['cpu_cores_required'] > 4:
                issues.append('Требует много CPU')
            if comp['ram_mb'] > 4096:
                issues.append('Требует много RAM')
            
            if issues:
                bottlenecks.append({
                    'component': comp['id'],
                    'type': comp['type'],
                    'issues': issues,
                    'metrics': {
                        'events_per_second': comp['events_per_second'],
                        'cpu_cores': comp['cpu_cores_required'],
                    },
                })
        
        return bottlenecks
    
    def _generate_recommendations(
        self, per_component: List[Dict],
        bottlenecks: List[Dict], resources: Dict,
    ) -> List[Dict]:
        recommendations = []
        
        historian = [c for c in per_component if c['type'] == 'historian']
        if historian and historian[0]['disk_gb_per_day'] > 10:
            recommendations.append({
                'priority': 'high',
                'component': 'historian',
                'recommendation': 'TimescaleDB с сжатием + retention policy',
                'reason': f"Данные: {historian[0]['disk_gb_per_day']} GB/день",
            })
        
        if resources['with_reserve']['network_mbps'] > 100:
            recommendations.append({
                'priority': 'high',
                'component': 'network',
                'recommendation': '1 Gbps сеть + VLAN segmentation',
                'reason': f"Требуется: {resources['with_reserve']['network_mbps']} Mbps",
            })
        
        recommendations.append({
            'priority': 'medium',
            'component': 'all',
            'recommendation': 'Мониторинг через Prometheus + Grafana',
            'reason': 'Проактивное обнаружение проблем',
        })
        
        return recommendations