"""
Генерация трудных отрицательных примеров.
"""
from typing import List, Dict
from loguru import logger

from src.deepseek.local_client import get_deepseek_client
from src.deepseek.prompts.hard_negatives import (
    HARD_NEGATIVES_SYSTEM,
    build_hard_negatives_prompt
)


class HardNegativeGenerator:
    """
    Генератор hard negatives для контрастивного обучения.
    """
    
    def __init__(self):
        self.client = get_deepseek_client()
        logger.info("HardNegativeGenerator инициализирован")
    
    def generate(
        self,
        positive_examples: List[str],
        n_per_example: int = 5
    ) -> List[Dict]:
        """
        Генерация hard negatives.
        
        Args:
            positive_examples: список корректных примеров
            n_per_example: количество negatives на пример
        
        Returns:
            Список триплетов (anchor, positive, negatives)
        """
        triplets = []
        
        for i, positive in enumerate(positive_examples):
            logger.info(f"Генерация {i+1}/{len(positive_examples)}")
            
            try:
                response = self.client.generate(
                    prompt=build_hard_negatives_prompt(positive, n_per_example),
                    system_prompt=HARD_NEGATIVES_SYSTEM,
                    temperature=0.3,
                    max_tokens=1024
                )
                
                negatives = self._parse_negatives(response)
                
                if negatives:
                    triplets.append({
                        'positive': positive,
                        'negatives': negatives
                    })
            
            except Exception as e:
                logger.error(f"Ошибка: {e}")
                continue
        
        logger.info(f"Сгенерировано {len(triplets)} триплетов")
        return triplets
    
    def _parse_negatives(self, response: str) -> List[Dict]:
        """Парсинг JSON с negatives."""
        import json
        
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start == -1 or end == 0:
                return []
            
            data = json.loads(response[start:end])
            return data.get('hard_negatives', [])
        
        except json.JSONDecodeError:
            return []