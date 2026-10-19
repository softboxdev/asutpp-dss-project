# scripts/test_local_setup.py
"""
Проверка полностью локального проекта.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def test_environment():
    """Проверка окружения."""
    print("=" * 60)
    print("ПРОВЕРКА ЛОКАЛЬНОГО ОКРУЖЕНИЯ")
    print("=" * 60)
    
    # 1. Проверка GPU
    import torch
    if torch.cuda.is_available():
        print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
        print(f"   VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
    else:
        print("❌ GPU недоступна")
        return False
    
    # 2. Проверка DeepSeek сервера
    try:
        from src.deepseek.local_client import get_deepseek_client
        client = get_deepseek_client()
        print(f"✅ DeepSeek сервер доступен")
        
        # Тестовый запрос
        response = client.generate(
            "Ответь одним словом: работает?",
            max_tokens=10
        )
        print(f"   Тест: {response[:50]}")
    
    except Exception as e:
        print(f"❌ DeepSeek недоступен: {e}")
        return False
    
    # 3. Проверка онтологии
    ontology_path = Path("data/ontology/asutp_ontology.json")
    if ontology_path.exists():
        print(f"✅ Онтология: {ontology_path}")
    else:
        print(f"❌ Онтология не найдена: {ontology_path}")
    
    # 4. Проверка директорий
    dirs = [
        "data/raw", "data/processed", "data/synthetic",
        "models/deepseek", "models/dacie", "results",
    ]
    for d in dirs:
        if Path(d).exists():
            print(f"✅ {d}")
        else:
            print(f"⚠️  {d} не существует")
            Path(d).mkdir(parents=True, exist_ok=True)
    
    print("\n" + "=" * 60)
    print("ПРОВЕРКА ЗАВЕРШЕНА УСПЕШНО")
    print("=" * 60)
    return True


if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1)