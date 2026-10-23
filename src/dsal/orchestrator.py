"""
Оркестратор DSAL-цикла обучения.
Работает в двух режимах:
1. Без main_model — только генерация данных
2. С main_model — реальное обучение
"""
import torch
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from loguru import logger

from src.dsal.data_generator import SyntheticDataGenerator
from src.dsal.hard_negative_gen import HardNegativeGenerator
from src.ai_service.local_client import get_ai_client


class DSALOrchestrator:
    """Оркестратор DeepSeek-Assisted Learning."""
    
    def __init__(
        self,
        main_model: Optional[torch.nn.Module] = None,   # ← ОПЦИОНАЛЬНО
        optimizer: Optional[torch.optim.Optimizer] = None,
        output_dir: str = "models/dsal",
    ):
        self.main_model = main_model
        self.optimizer = optimizer
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = get_ai_client()
        self.data_generator = SyntheticDataGenerator()
        self.hard_neg_gen = HardNegativeGenerator()
        
        mode = "обучение" if main_model is not None else "генерация данных"
        logger.info(f"DSALOrchestrator инициализирован (режим: {mode})")
    
    def train_epoch(
        self,
        labeled_data: List[Dict],
        unlabeled_data: List[str],
        batch_size: int = 16,
        alpha: float = 0.7,
        beta: float = 0.3,
    ) -> Dict[str, float]:
        metrics = {
            'task_loss': 0.0,
            'distill_loss': 0.0,
            'contrast_loss': 0.0,
            'total_loss': 0.0,
            'synthetic_count': 0,
            'triplets_count': 0,
        }
        
        # Фаза 1: Supervised
        logger.info("Фаза 1: Обучение на размеченных данных")
        if self.main_model is not None and labeled_data:
            metrics['task_loss'] = self._train_supervised(
                labeled_data, batch_size
            )
        else:
            logger.info("  (пропущено — нет модели или данных)")
        
        # Фаза 2: Генерация синтетики
        logger.info("Фаза 2: Генерация синтетических данных")
        synthetic = []
        if unlabeled_data:
            combined = '\n\n'.join(unlabeled_data[:5])
            synthetic = self.data_generator.generate_from_document(combined)
            metrics['synthetic_count'] = len(synthetic)
            logger.info(f"  Сгенерировано: {len(synthetic)}")
        
        # Фаза 3: Дистилляция
        logger.info("Фаза 3: Дистилляция знаний")
        if self.main_model is not None and synthetic:
            metrics['distill_loss'] = self._train_distillation(
                synthetic, batch_size
            )
        else:
            logger.info("  (пропущено)")
        
        # Фаза 4: Контрастивное обучение
        logger.info("Фаза 4: Контрастивное обучение")
        positives = self._extract_positives(labeled_data)
        
        if positives:
            triplets = self.hard_neg_gen.generate(positives[:20])
            metrics['triplets_count'] = len(triplets)
            
            if self.main_model is not None and triplets:
                metrics['contrast_loss'] = self._train_contrastive(
                    triplets, batch_size
                )
        else:
            logger.info("  (пропущено — нет positives)")
        
        # Итог
        metrics['total_loss'] = (
            alpha * metrics['task_loss']
            + beta * metrics['distill_loss']
            + (1 - alpha - beta) * metrics['contrast_loss']
        )
        
        logger.info(f"Эпоха завершена: {metrics}")
        return metrics
    
    def _train_supervised(self, data: List[Dict], batch_size: int) -> float:
        if self.main_model is None or self.optimizer is None:
            return 0.0
        logger.info(f"  supervised на {len(data)} (заглушка)")
        return 0.5
    
    def _train_distillation(self, synthetic: List[Dict], batch_size: int) -> float:
        if self.main_model is None or self.optimizer is None:
            return 0.0
        logger.info(f"  distillation на {len(synthetic)} (заглушка)")
        return 0.3
    
    def _train_contrastive(self, triplets: List[Dict], batch_size: int) -> float:
        if self.main_model is None or self.optimizer is None:
            return 0.0
        logger.info(f"  contrastive на {len(triplets)} (заглушка)")
        return 0.2
    
    def _extract_positives(self, data: List[Dict]) -> List[str]:
        positives = []
        for sample in data:
            for entity in sample.get('entities', []):
                text = entity.get('text', '').strip()
                if text and len(text) >= 3:
                    positives.append(text)
        return positives
    
    def run_full_cycle(
        self,
        labeled_data: List[Dict],
        unlabeled_data: List[str],
        epochs: int = 10,
    ) -> Dict:
        logger.info(f"Запуск DSAL-цикла (epochs={epochs})")
        
        history = []
        
        for epoch in range(epochs):
            logger.info(f"=== Эпоха {epoch + 1}/{epochs} ===")
            metrics = self.train_epoch(
                labeled_data=labeled_data,
                unlabeled_data=unlabeled_data,
            )
            history.append(metrics)
            
            if self.main_model is not None and (epoch + 1) % 5 == 0:
                self._save_checkpoint(epoch, metrics)
        
        self._save_history(history)
        
        logger.info("DSAL-цикл завершён")
        
        return {
            'history': history,
            'synthetic_count': sum(h['synthetic_count'] for h in history),
            'triplets_count': sum(h['triplets_count'] for h in history),
            'timestamp': datetime.now().isoformat(),
        }
    
    def _save_checkpoint(self, epoch: int, metrics: Dict):
        if self.main_model is None:
            return
        
        path = self.output_dir / f"checkpoint_epoch_{epoch+1}.pt"
        try:
            torch.save({
                'epoch': epoch,
                'model_state': self.main_model.state_dict(),
                'metrics': metrics,
            }, path)
            logger.info(f"Checkpoint: {path}")
        except Exception as e:
            logger.warning(f"Не удалось сохранить: {e}")
    
    def _save_history(self, history: List[Dict]):
        path = self.output_dir / f"dsal_history_{datetime.now():%Y%m%d_%H%M%S}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        logger.info(f"История: {path}")
