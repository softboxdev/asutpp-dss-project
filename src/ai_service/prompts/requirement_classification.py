"""Промпт для классификации требований."""

REQUIREMENT_CLASSIFICATION_SYSTEM = """Ты — эксперт по АСУ ТП.
Классифицируй требования по категориям. Отвечай JSON."""


def build_requirement_classification_prompt(text: str) -> str:
    return f"""Классифицируй требования из фрагмента ТЗ:

\"\"\"
{text[:3000]}
\"\"\"

Категории:
- functional: функциональные
- safety: безопасность (SIL)
- performance: производительность
- reliability: надежность
- interface: интерфейсы
- constraint: ограничения

Верни JSON:
{{
    "requirements": [
        {{
            "text": "...",
            "category": "functional|safety|...",
            "priority": "high|medium|low",
            "confidence": 0.95
        }}
    ]
}}"""