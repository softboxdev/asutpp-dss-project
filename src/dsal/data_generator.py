"""
Генератор синтетических размеченных данных с помощью DeepSeek.
"""
import json
from pathlib import Path
from typing import List, Dict, Tuple
from loguru import logger

from src.ai_service.local_client import get_ai_client
from src.ai_service.prompts.entity_extraction import (
    ENTITY_EXTRACTION_SYSTEM,
    build_entity_extraction_prompt
)


class SyntheticDataGenerator:
    """
    Генерация размеченных примеров из неразмеченных ТЗ.
    """
    
    def __init__(
        self,
        confidence_threshold: float = 0.85,
        output_dir: str = "data/synthetic"
    ):
        self.client = get_ai_client()
        self.confidence_threshold = confidence_threshold
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("SyntheticDataGenerator инициализирован")
    
    def generate_from_document(
        self,
        document_text: str,
        chunk_size: int = 2000
    ) -> List[Dict]:
        """
        Генерация размеченных примеров из документа.
        """
        # Разбиение на фрагменты
        chunks = self._chunk_document(document_text, chunk_size)
        logger.info(f"Обработка {len(chunks)} фрагментов")
        
        synthetic_samples = []
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Фрагмент {i+1}/{len(chunks)}")
            
            try:
                # Генерация через DeepSeek
                response = self.client.generate(
                    prompt=build_entity_extraction_prompt(chunk),
                    system_prompt=ENTITY_EXTRACTION_SYSTEM,
                    temperature=0.1,
                    max_tokens=2048
                )
                
                # Парсинг
                entities = self._parse_response(response)
                
                if entities:
                    # Фильтрация по уверенности
                    high_confidence = [
                        e for e in entities
                        if e.get('confidence', 0) >= self.confidence_threshold
                    ]
                    
                    if high_confidence:
                        synthetic_samples.append({
                            'text': chunk,
                            'entities': high_confidence,
                            'source': 'deepseek',
                            'chunk_id': i
                        })
            
            except Exception as e:
                logger.error(f"Ошибка обработки фрагмента {i}: {e}")
                continue
        
        logger.info(f"Сгенерировано {len(synthetic_samples)} примеров")
        
        # Сохранение
        self._save_samples(synthetic_samples)
        
        return synthetic_samples
    
    def _chunk_document(
        self,
        text: str,
        chunk_size: int
    ) -> List[str]:
        """Разбиение документа на фрагменты по абзацам."""
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < chunk_size:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _parse_response(self, response: str) -> List[Dict]:
        """Парсинг JSON из ответа."""
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end == 0:
                return []
            
            data = json.loads(response[start:end])
            return data.get('entities', [])
        
        except json.JSONDecodeError:
            return []
    
    def _save_samples(self, samples: List[Dict]):
        """Сохранение сгенерированных данных."""
        output_file = self.output_dir / "generated_samples.jsonl"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for sample in samples:
                f.write(json.dumps(sample, ensure_ascii=False) + '\n')
        
        logger.info(f"Данные сохранены: {output_file}")