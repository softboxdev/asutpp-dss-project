"""Примеры проектирования."""
from typing import Dict, List
from .base import ReportSection


class ArchitectureExamplesGenerator(ReportSection):
    """Генерирует примеры кода и конфигурации."""
    
    name = "architecture_examples"
    title = "Примеры проектирования"
    order = 40
    
    def build(self, pipeline_result, context: Dict) -> Dict:
        if not pipeline_result.architectures:
            return {'error': 'no_architectures'}
        
        arch = pipeline_result.architectures[0]
        pattern = arch.get('pattern', 'layered')
        
        return {
            'pattern': pattern,
            'structure': self._structure(pattern, arch),
            'docker_compose': self._docker_compose(pattern),
            'code_snippets': self._code_examples(pattern),
            'integration': self._integration_examples(),
            'deployment': self._deployment_example(context),
        }
    
    def _structure(self, pattern: str, arch: Dict) -> Dict:
        return {
            'pattern': pattern,
            'total_components': len(arch.get('components', [])),
            'hierarchy': self._hierarchy(pattern, arch),
        }
    
    def _hierarchy(self, pattern: str, arch: Dict) -> List[Dict]:
        if pattern == 'layered':
            return [
                {'level': 1, 'name': 'Presentation', 
                 'components': ['hmi', 'ui']},
                {'level': 2, 'name': 'Business Logic',
                 'components': ['business_logic', 'controller']},
                {'level': 3, 'name': 'Data Access',
                 'components': ['historian', 'database']},
                {'level': 4, 'name': 'Data Sources',
                 'components': ['sensor_adapter']},
            ]
        elif pattern == 'event_driven':
            return [
                {'level': 1, 'name': 'Event Sources',
                 'components': ['sensor_adapter', 'controller']},
                {'level': 2, 'name': 'Event Bus',
                 'components': ['event_bus']},
                {'level': 3, 'name': 'Event Processors',
                 'components': ['business_logic', 'historian']},
                {'level': 4, 'name': 'Event Consumers',
                 'components': ['hmi']},
            ]
        return []
    
    def _docker_compose(self, pattern: str) -> str:
        if pattern == 'event_driven':
            return '''version: '3.9'
services:
  rabbitmq:
    image: rabbitmq:3-management
    ports: ["5672:5672", "15672:15672"]
  
  sensor-publisher:
    build: ./sensor_publisher
    depends_on: [rabbitmq]
  
  event-processor:
    build: ./event_processor
    depends_on: [rabbitmq]
  
  historian:
    image: timescale/timescaledb:latest
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: historian
      POSTGRES_USER: asutp
      POSTGRES_PASSWORD: secret
    volumes:
      - historian_data:/var/lib/postgresql/data

volumes:
  historian_data:'''
        
        return '''version: '3.9'
services:
  sensor-adapter:
    build: ./sensor_adapter
    ports: ["8010:8000"]
    environment:
      - MODBUS_HOST=plc.local
  
  controller:
    build: ./controller
    ports: ["8011:8000"]
    depends_on: [sensor-adapter]
  
  historian:
    image: timescale/timescaledb:latest
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: historian
      POSTGRES_USER: asutp
      POSTGRES_PASSWORD: secret
  
  hmi:
    build: ./hmi
    ports: ["3000:3000"]
    depends_on: [controller, historian]'''
    
    def _code_examples(self, pattern: str) -> Dict:
        return {
            'sensor_reader': '''# sensor_adapter/modbus_reader.py
from pymodbus.client import ModbusTcpClient
from loguru import logger


class TemperatureSensor:
    """Чтение температуры через Modbus TCP."""
    
    def __init__(self, host: str, port: int = 502):
        self.client = ModbusTcpClient(host, port)
        self.client.connect()
        logger.info(f"Modbus: {host}:{port}")
    
    def read_temperature(self) -> float:
        """Чтение регистра."""
        result = self.client.read_holding_registers(
            address=0, count=1, unit=1
        )
        if result.isError():
            logger.error(f"Modbus error: {result}")
            return -1.0
        
        raw = result.registers[0]
        return raw / 10.0  # 0.1°C resolution
    
    def close(self):
        self.client.close()''',
            
            'pid_controller': '''# controller/pid.py
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PIDController:
    """PID-регулятор для АСУ ТП."""
    
    kp: float = 2.0
    ki: float = 0.1
    kd: float = 0.05
    dt: float = 0.1
    setpoint: float = 0.0
    
    def __post_init__(self):
        self.integral = 0.0
        self.prev_error = 0.0
    
    def compute(self, measured: float) -> float:
        """Вычислить управляющее воздействие."""
        error = self.setpoint - measured
        
        # Интегральная часть (с защитой от windup)
        self.integral += error * self.dt
        self.integral = max(-100, min(100, self.integral))
        
        # Дифференциальная часть
        derivative = (error - self.prev_error) / self.dt
        self.prev_error = error
        
        # Выход
        output = (self.kp * error + 
                  self.ki * self.integral + 
                  self.kd * derivative)
        
        # Ограничение
        return max(0, min(100, output))''',
            
            'historian_writer': '''# historian/writer.py
import asyncpg
from datetime import datetime
from typing import List
import asyncio


class HistorianWriter:
    """Запись в TimescaleDB."""
    
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(self.dsn, min_size=2, max_size=10)
    
    async def write_batch(self, points: List[dict]):
        """Пакетная запись."""
        async with self.pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO metrics (time, sensor_id, value, quality)
                VALUES ($1, $2, $3, $4)
                """,
                [(p['time'], p['sensor_id'], p['value'], p['quality'])
                 for p in points]
            )
    
    async def query_range(self, sensor_id: str, 
                          start: datetime, end: datetime):
        """Запрос диапазона."""
        async with self.pool.acquire() as conn:
            return await conn.fetch(
                """
                SELECT time, value FROM metrics
                WHERE sensor_id = $1 
                  AND time BETWEEN $2 AND $3
                ORDER BY time
                """,
                sensor_id, start, end
            )''',
        }
    
    def _integration_examples(self) -> Dict:
        return {
            'opc_ua': '''# integration/opcua_client.py
from asyncua import Client
from loguru import logger


class OPCUAClient:
    """Клиент для SCADA через OPC UA."""
    
    def __init__(self, url: str):
        self.url = url
        self.client = None
    
    async def connect(self):
        self.client = Client(url=self.url)
        await self.client.connect()
        logger.info(f"OPC UA: {self.url}")
    
    async def read_node(self, node_id: str):
        node = self.client.get_node(node_id)
        return await node.read_value()
    
    async def write_node(self, node_id: str, value):
        node = self.client.get_node(node_id)
        await node.write_value(value)''',
            
            'mes_rest': '''# integration/mes_client.py
import httpx
from loguru import logger


class MESClient:
    """Клиент для MES через REST."""
    
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    async def send_production_data(self, data: dict):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/production",
                json=data,
                headers=self.headers,
                timeout=10.0,
            )
            logger.info(f"MES: {response.status_code}")
            return response.json()''',
        }
    
    def _deployment_example(self, context: Dict) -> Dict:
        team = context.get('team_size', 5)
        
        return {
            'recommended': 'on-premise' if team < 10 else 'hybrid',
            'team_size': team,
            'environments': [
                {'name': 'development', 'config': 'docker compose'},
                {'name': 'staging', 'config': 'k8s, 3 nodes'},
                {'name': 'production', 'config': 'k8s, 6+ nodes with redundancy'},
            ],
            'rollout_plan': [
                {'phase': 1, 'duration': '2 weeks', 
                 'components': ['sensor_adapter', 'controller']},
                {'phase': 2, 'duration': '3 weeks',
                 'components': ['historian', 'hmi']},
                {'phase': 3, 'duration': '2 weeks',
                 'components': ['business_logic', 'integrations']},
            ],
        }