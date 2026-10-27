"""DACIE Domain-Adaptive Compositional Information Extractor — извлечение сущностей из ТЗ."""
import json
import re
from pathlib import Path
from typing import List, Dict, Any
from loguru import logger

from src.ai_service.local_client import get_ai_client


class DACIE:
    """Нейро-символьный извлекатель сущностей."""
    
    def __init__(self, use_ai: bool = True):
        self.use_ai = use_ai
        self.ontology = self._load_ontology()
        
        self.ai_client = None
        if use_ai:
            try:
                self.ai_client = get_ai_client()
                logger.info("AI Service подключён")
            except Exception as e:
                logger.warning(f"AI Service недоступен: {e}")
                self.use_ai = False
        
        logger.info(f"DACIE готов: {len(self.ontology['entity_types'])} типов")
    
    def _load_ontology(self) -> Dict:
        path = Path("data/ontology/asutp_ontology.json")
        if not path.exists():
            raise FileNotFoundError(f"Онтология не найдена: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def build_document_graph(self, text: str) -> Dict:
        sections = []
        lines = text.split('\n')
        current = None
        section_id = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if re.match(r'^\d+(\.\d+)*\.?\s+[А-ЯЁ]', line):
                if current is not None:
                    sections.append(current)
                current = {
                    'id': section_id,
                    'title': line,
                    'text': line,
                    'level': line.count('.') + 1 if '.' in line[:6] else 1,
                }
                section_id += 1
            elif current is not None:
                current['text'] += '\n' + line
        
        if current is not None:
            sections.append(current)
        
        return {'sections': sections, 'num_sections': len(sections)}
    
    def extract_symbolic(self, text: str) -> List[Dict]:
        entities = []
        text_lower = text.lower()
        for concept, rules in self.ontology['concepts'].items():
            for keyword in rules['keywords']:
                if keyword.lower() in text_lower:
                    entities.append({
                        'text': keyword,
                        'type': concept,
                        'confidence': 0.75,
                        'source': 'symbolic',
                    })
                    break
        return entities
    
    def extract_ai(self, text: str) -> List[Dict]:
        if not self.use_ai or not self.ai_client:
            return []
        
        from src.ai_service.prompts.entity_extraction import (
            ENTITY_EXTRACTION_SYSTEM, build_entity_extraction_prompt
        )
        
        try:
            response = self.ai_client.generate(
                prompt=build_entity_extraction_prompt(text),
                system_prompt=ENTITY_EXTRACTION_SYSTEM,
                temperature=0.1,
                max_tokens=4096,
            )
            return self._parse_json(response)
        except Exception as e:
            logger.error(f"AI ошибка: {e}")
            return []
    
    def _parse_json(self, response: str) -> List[Dict]:
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end == 0:
                return []
            data = json.loads(response[start:end])
            for e in data.get('entities', []):
                e['source'] = 'ai'
            return data.get('entities', [])
        except json.JSONDecodeError:
            return []
    
    def process(self, text: str) -> Dict[str, Any]:
        logger.info("DACIE: обработка")
        
        graph = self.build_document_graph(text)
        symbolic = self.extract_symbolic(text)
        logger.info(f"Символьных: {len(symbolic)}")
        
        ai_entities = []
        if self.use_ai:
            ai_entities = self.extract_ai(text)
            logger.info(f"AI: {len(ai_entities)}")
        
        merged = self._merge(symbolic, ai_entities)
        logger.info(f"Итого: {len(merged)}")
        
        return {'graph': graph, 'entities': merged}
    
    def _merge(self, symbolic: List, ai: List) -> List:
        merged = {}
        for e in symbolic + ai:
            key = (e['text'].lower(), e['type'])
            if key not in merged or \
               e.get('confidence', 0) > merged[key].get('confidence', 0):
                merged[key] = e
        return list(merged.values())
