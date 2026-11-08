"""Базовые классы для модуля отчётов."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import json
from loguru import logger


class ReportSection(ABC):
    """Базовый класс секции отчёта."""
    
    name: str = "section"
    title: str = "Секция"
    order: int = 100
    
    def __init__(self, output_dir: Path = None):
        self.output_dir = Path(output_dir or "results/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger
    
    @abstractmethod
    def build(self, pipeline_result, context: Dict) -> Dict[str, Any]:
        """Построить секцию. Возвращает dict с данными."""
        pass
    
    def to_json(self, data: Dict, filename: str = None) -> Path:
        """Экспорт в JSON."""
        if filename is None:
            filename = f"{self.name}.json"
        path = self.output_dir / filename
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        self.logger.info(f"JSON: {path}")
        return path
    
    def to_markdown(self, data: Dict) -> str:
        """Экспорт в Markdown (переопределяется в наследниках)."""
        lines = [f"## {self.title}", ""]
        lines.append("```json")
        lines.append(json.dumps(data, ensure_ascii=False, indent=2, default=str))
        lines.append("```")
        return '\n'.join(lines)
    
    def to_mermaid(self, data: Dict) -> str:
        """Экспорт в Mermaid (опционально)."""
        return ""