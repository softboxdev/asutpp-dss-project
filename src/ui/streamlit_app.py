"""Streamlit UI."""
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="АСУ ТП Архитектура DSS", page_icon="🏭", layout="wide")
st.title("🏭 СППР для проектирования архитектуры ПО АСУ ТП")

with st.sidebar:
    st.header("⚙️ Контекст")
    team_size = st.slider("Команда", 1, 30, 5)
    budget = st.slider("Бюджет (млн ₽)", 1, 50, 10)
    timeline = st.slider("Срок (мес)", 1, 24, 6)
    sil = st.selectbox("SIL", [0, 1, 2, 3, 4], 2)
    real_time = st.checkbox("Real-time", True)
    use_ai = st.checkbox("Использовать AI", True)

col1, col2 = st.columns(2)

with col1:
    st.header("📄 ТЗ")
    default = Path("data/test_examples/chemical_reactor_tz.txt")
    tz_text = default.read_text(encoding='utf-8') if default.exists() else ""
    tz_text = st.text_area("Текст", tz_text, height=400)
    
    if st.button("🚀 Анализ", type="primary"):
        if not tz_text.strip():
            st.error("Введите ТЗ")
        else:
            with st.spinner("Анализ..."):
                from src.pipeline.orchestrator import ArchitectureDesignPipeline
                ctx = {
                    'team_size': team_size,
                    'budget_million_rub': budget,
                    'timeline_months': timeline,
                    'safety_level_sil': sil,
                    'real_time_critical': real_time,
                    'num_external_systems': 3,
                    'has_scada_integration': True,
                    'has_mes_integration': False,
                }
                pipeline = ArchitectureDesignPipeline(use_ai=use_ai)
                st.session_state['result'] = pipeline.run(tz_text, ctx, verbose=False)

with col2:
    st.header("📊 Результаты")
    if 'result' in st.session_state:
        r = st.session_state['result']
        st.metric("Сущностей", len(r.requirements.get('entities', [])))
        
        st.subheader("Паттерны")
        for p in r.patterns[:3]:
            st.progress(p['confidence'], text=f"{p['pattern']}: {p['confidence']:.1%}")
        
        if r.quality_assessment:
            st.metric("Score", f"{r.quality_assessment['overall_score']:.4f}")
        
        st.write(f"⏱️ {r.timings.get('total', 0):.2f}с")
    else:
        st.info("Запустите анализ")
