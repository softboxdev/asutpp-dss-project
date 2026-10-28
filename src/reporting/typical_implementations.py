"""Типовые реализации компонентов."""
from typing import Dict, List
from .base import ReportSection


class TypicalImplementationsLibrary(ReportSection):
    """Библиотека готовых реализаций."""
    
    name = "typical_implementations"
    title = "Типовые реализации"
    order = 50
    
    def __init__(self, output_dir=None):
        super().__init__(output_dir)
        self.library = self._load_library()
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        pattern = pipeline_result.patterns[0]['pattern'] if pipeline_result.patterns else 'layered'
        
        return {
            'for_pattern': pattern,
            'total_count': len(self.library),
            'implementations': list(self.library.values()),
        }
    
    def _load_library(self) -> Dict:
        return {
            'pid_controller': {
                'name': 'PID-регулятор',
                'category': 'control',
                'typical_for': ['температура', 'давление', 'расход'],
                'description': 'Классический PID-регулятор для технологических параметров',
                'standards': ['IEC 61131-3', 'ISA-88'],
                'implementation': '''```python
class PIDController:
    def __init__(self, kp, ki, kd, dt=0.1):
        self.kp, self.ki, self.kd = kp, ki, kd
        self.dt = dt
        self.integral = 0
        self.prev_error = 0
    
    def compute(self, setpoint, measured):
        error = setpoint - measured
        self.integral += error * self.dt
        derivative = (error - self.prev_error) / self.dt
        self.prev_error = error
        return self.kp * error + self.ki * self.integral + self.kd * derivative
```''',
            },
            'safety_interlock': {
                'name': 'Блокировка безопасности (SIL)',
                'category': 'safety',
                'typical_for': ['аварийные ситуации', 'SIL 2/3'],
                'description': 'Реализация блокировки по стандарту IEC 61508',
                'standards': ['IEC 61508', 'IEC 61511'],
                'implementation': '''```python
class SafetyInterlock:
    def __init__(self, sil_level=2):
        self.sil_level = sil_level
        self.trip_conditions = []
        self.is_tripped = False
    
    def add_trip_condition(self, condition_fn, description):
        self.trip_conditions.append({
            'fn': condition_fn,
            'desc': description,
        })
    
    def check(self, measurements):
        for tc in self.trip_conditions:
            if tc['fn'](measurements):
                self.trip(tc['desc'])
                return True
        return False
    
    def trip(self, reason):
        self.is_tripped = True
        self.emergency_shutdown(reason)
```''',
            },
            'historian_buffer': {
                'name': 'Буфер Historian',
                'category': 'data',
                'typical_for': ['хранение временных рядов'],
                'description': 'Буферизация данных с записью в TimescaleDB',
                'standards': ['ISA-95'],
                'implementation': '''```python
from collections import deque


class HistorianBuffer:
    def __init__(self, buffer_size=1000):
        self.buffer = deque(maxlen=buffer_size)
    
    def add(self, data_point):
        self.buffer.append(data_point)
    
    def flush_to_db(self, db_conn):
        if not self.buffer:
            return
        batch = list(self.buffer)
        self.buffer.clear()
        db_conn.insert_batch(batch)
```''',
            },
            'opc_ua_client': {
                'name': 'OPC UA клиент',
                'category': 'integration',
                'typical_for': ['SCADA', 'MES', 'ERP'],
                'description': 'Подключение к OPC UA серверу',
                'standards': ['IEC 62541'],
                'implementation': '''```python
from asyncua import Client

class OPCUAClient:
    def __init__(self, url):
        self.url = url
        self.client = None
    
    async def connect(self):
        self.client = Client(url=self.url)
        await self.client.connect()
    
    async def read(self, node_id):
        node = self.client.get_node(node_id)
        return await node.read_value()
```''',
            },
            'modbus_tcp': {
                'name': 'Modbus TCP клиент',
                'category': 'integration',
                'typical_for': ['ПЛК', 'датчики'],
                'description': 'Клиент Modbus TCP для чтения регистров',
                'standards': ['Modbus Spec'],
                'implementation': '''```python
from pymodbus.client import ModbusTcpClient

class ModbusReader:
    def __init__(self, host, port=502):
        self.client = ModbusTcpClient(host, port)
    
    def read_registers(self, address, count):
        return self.client.read_holding_registers(address, count)
    
    def write_register(self, address, value):
        return self.client.write_register(address, value)
```''',
            },
            'alarm_manager': {
                'name': 'Менеджер алармов',
                'category': 'safety',
                'typical_for': ['уведомления операторов'],
                'description': 'Управление алармами по ISA-18.2',
                'standards': ['ISA-18.2'],
                'implementation': '''```python
class AlarmManager:
    def __init__(self):
        self.alarms = []
        self.active = {}
    
    def raise_alarm(self, alarm_id, severity, message):
        alarm = {
            'id': alarm_id,
            'severity': severity,
            'message': message,
            'timestamp': datetime.now(),
        }
        self.alarms.append(alarm)
        self.active[alarm_id] = alarm
        self.notify_operators(alarm)
```''',
            },
            'data_validator': {
                'name': 'Валидатор данных',
                'category': 'data',
                'typical_for': ['проверка диапазонов', 'качество данных'],
                'description': 'Валидация входящих данных по правилам',
                'standards': ['ISA-101'],
                'implementation': '''```python
class DataValidator:
    def __init__(self):
        self.rules = []
    
    def add_range_rule(self, param, min_val, max_val):
        self.rules.append({
            'param': param,
            'min': min_val,
            'max': max_val,
        })
    
    def validate(self, data):
        for rule in self.rules:
            val = data.get(rule['param'])
            if val is None:
                return False, f"Missing {rule['param']}"
            if not (rule['min'] <= val <= rule['max']):
                return False, f"{rule['param']}={val} out of range"
        return True, "OK"
```''',
            },
        }
    
    def get_by_category(self, category: str) -> List[Dict]:
        return [v for v in self.library.values() if v['category'] == category]
    
    def get_by_standard(self, standard: str) -> List[Dict]:
        return [v for v in self.library.values() 
                if standard in v.get('standards', [])]