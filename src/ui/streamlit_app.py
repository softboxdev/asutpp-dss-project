"""Streamlit UI для СППР АСУ ТП.

Расширенная версия с 18 секциями отчёта.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
from datetime import datetime

# ============================================================
# НАСТРОЙКА
# ============================================================

st.set_page_config(
    page_title="АСУ ТП Архитектура DSS",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS для красоты
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 1rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR — КОНТЕКСТ ПРОЕКТА
# ============================================================

with st.sidebar:
    st.title("⚙️ Контекст проекта")
    
    st.subheader("Параметры")
    team_size = st.slider("Размер команды", 1, 30, 8, 
                          help="Количество FTE")
    budget = st.slider("Бюджет (млн ₽)", 1, 50, 15)
    timeline = st.slider("Срок (месяцев)", 1, 24, 8)
    
    st.subheader("Безопасность")
    sil = st.selectbox("Уровень SIL", [0, 1, 2, 3, 4], 2)
    real_time = st.checkbox("Real-time критические", True)
    
    st.subheader("Интеграции")
    ext_systems = st.number_input("Внешних систем", 0, 20, 3)
    has_scada = st.checkbox("SCADA", True)
    has_mes = st.checkbox("MES", True)
    has_erp = st.checkbox("ERP", False)
    
    st.subheader("Технологический объект")
    io_points = st.number_input("Точек ввода-вывода", 10, 10000, 500)
    control_loops = st.number_input("Регулирующих контуров", 1, 500, 25)
    data_volume = st.number_input("Данных (ГБ/день)", 0.1, 1000.0, 10.0)
    
    st.subheader("AI")
    use_ai = st.checkbox("Использовать AI", True)
    if use_ai:
        ai_model = st.selectbox(
            "Модель",
            ["deepseek-r1:7b", "deepseek-r1:1.5b"],
        )
    
    st.subheader("Отчёт")
    full_report = st.checkbox("Полный отчёт (18 секций)", True)
    
    st.divider()
    st.caption(f"Версия 0.2.0 | {datetime.now():%Y-%m-%d}")


# ============================================================
# ЗАГОЛОВОК
# ============================================================

st.markdown('<div class="main-header">🏭 СППР для проектирования архитектуры ПО АСУ ТП</div>', 
            unsafe_allow_html=True)

st.caption("Система поддержки принятия решений для задачи проектирования программного обеспечения в области автоматизации")

# ============================================================
# ВКЛАДКИ
# ============================================================

tab_input, tab_results, tab_topology, tab_load, tab_plan, tab_risks, tab_export = st.tabs([
    "📄 Ввод ТЗ",
    "📊 Результаты",
    "🗺️ Топология",
    "📈 Нагрузка",
    "📅 План работ",
    "⚠️ Риски",
    "💾 Экспорт",
])


# ============================================================
# ВКЛАДКА 1: ВВОД ТЗ
# ============================================================

with tab_input:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Техническое задание")
        
        # Загрузка файла или текст
        uploaded = st.file_uploader("Загрузите ТЗ (txt)", type=['txt', 'md'])
        
        if uploaded:
            tz_text = uploaded.read().decode('utf-8')
        else:
            default = Path("data/test_examples/chemical_reactor_tz.txt")
            tz_text = default.read_text(encoding='utf-8') if default.exists() else ""
        
        tz_text = st.text_area(
            "Текст ТЗ",
            tz_text,
            height=500,
            help="Вставьте текст технического задания",
        )
        
        col_btn1, col_btn2 = st.columns([1, 1])
        
        with col_btn1:
            if st.button("🚀 Запустить анализ", type="primary", use_container_width=True):
                if not tz_text.strip():
                    st.error("❌ Введите ТЗ")
                else:
                    with st.spinner("⏳ Анализ..."):
                        from src.pipeline.orchestrator import ArchitectureDesignPipeline
                        
                        context = {
                            'team_size': team_size,
                            'budget_million_rub': budget,
                            'timeline_months': timeline,
                            'safety_level_sil': sil,
                            'real_time_critical': real_time,
                            'num_external_systems': ext_systems,
                            'has_scada_integration': has_scada,
                            'has_mes_integration': has_mes,
                            'has_erp_integration': has_erp,
                            'num_io_points': io_points,
                            'num_control_loops': control_loops,
                            'data_volume_gb_per_day': data_volume,
                        }
                        
                        pipeline = ArchitectureDesignPipeline(use_ai=use_ai)
                        result = pipeline.run(tz_text, context, verbose=False)
                        st.session_state['result'] = result
                        st.session_state['context'] = context
                        
                        # Полный отчёт
                        if full_report:
                            from src.reporting import ExtendedReportBuilder
                            builder = ExtendedReportBuilder()
                            report = builder.build(result, context)
                            st.session_state['report'] = report
                        
                        st.success("✅ Анализ завершён")
                        st.rerun()
        
        with col_btn2:
            if st.button("🔄 Очистить", use_container_width=True):
                st.session_state.clear()
                st.rerun()
    
    with col2:
        st.subheader("📊 Сводка контекста")
        
        st.metric("Команда", f"{team_size} FTE")
        st.metric("Бюджет", f"{budget} млн ₽")
        st.metric("Срок", f"{timeline} мес")
        st.metric("SIL", str(sil))
        st.metric("I/O точек", str(io_points))
        st.metric("Контуров", str(control_loops))


# ============================================================
# ВКЛАДКА 2: РЕЗУЛЬТАТЫ
# ============================================================

with tab_results:
    if 'result' not in st.session_state:
        st.info("👈 Запустите анализ на вкладке «Ввод ТЗ»")
    else:
        r = st.session_state['result']
        ctx = st.session_state.get('context', {})
        
        # === МЕТРИКИ ===
        st.markdown('<div class="section-header">📊 Ключевые метрики</div>', 
                    unsafe_allow_html=True)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Сущностей", len(r.requirements.get('entities', [])))
        with col2:
            st.metric("Паттернов", len(r.patterns))
        with col3:
            top_pattern = r.patterns[0]['pattern'] if r.patterns else '—'
            st.metric("Топ-паттерн", top_pattern.upper())
        with col4:
            score = r.quality_assessment.get('overall_score', 0)
            st.metric("Score", f"{score:.4f}")
        with col5:
            st.metric("Время", f"{r.timings.get('total', 0):.2f}с")
        
        st.divider()
        
        # === СУЩНОСТИ ===
        st.markdown('<div class="section-header">📋 Извлечённые сущности</div>', 
                    unsafe_allow_html=True)
        
        entities = r.requirements.get('entities', [])
        
        if entities:
            # Группировка по типу
            entity_types = {}
            for e in entities:
                t = e.get('type', 'unknown')
                entity_types[t] = entity_types.get(t, 0) + 1
            
            # График
            col1, col2 = st.columns([1, 1])
            
            with col1:
                df_types = pd.DataFrame({
                    'Тип': list(entity_types.keys()),
                    'Количество': list(entity_types.values()),
                })
                fig = px.pie(df_types, values='Количество', names='Тип',
                            title='Распределение по типам')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                df_sources = pd.DataFrame([
                    {'Источник': e.get('source', 'unknown'),
                     'Тип': e.get('type', '')}
                    for e in entities
                ])
                if not df_sources.empty:
                    source_counts = df_sources['Источник'].value_counts()
                    fig = px.bar(
                        x=source_counts.index,
                        y=source_counts.values,
                        labels={'x': 'Источник', 'y': 'Количество'},
                        title='Источники сущностей',
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Таблица
            df_entities = pd.DataFrame([
                {
                    'Тип': e.get('type', ''),
                    'Текст': e.get('text', '')[:80],
                    'Источник': e.get('source', ''),
                    'Уверенность': f"{e.get('confidence', 0):.2f}",
                }
                for e in entities[:30]
            ])
            st.dataframe(df_entities, use_container_width=True, height=300)
        else:
            st.warning("Сущности не найдены")
        
        st.divider()
        
        # === ПАТТЕРНЫ ===
        st.markdown('<div class="section-header">🏗️ Архитектурные паттерны</div>', 
                    unsafe_allow_html=True)
        
        if r.patterns:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Bar chart
                df_patterns = pd.DataFrame([
                    {'Паттерн': p['pattern'], 'Уверенность': p['confidence']}
                    for p in r.patterns
                ])
                fig = px.bar(df_patterns, x='Уверенность', y='Паттерн',
                            orientation='h', title='Рекомендованные паттерны',
                            color='Уверенность', color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Детали топ-паттерна
                top = r.patterns[0]
                st.markdown(f"**Топ-паттерн:** `{top['pattern']}`")
                st.progress(top['confidence'], 
                           text=f"Уверенность: {top['confidence']:.1%}")
                
                # Описание из patterns_explorer
                if 'report' in st.session_state:
                    rep = st.session_state['report']
                    patterns_info = rep.get('patterns', {}).get('details', {})
                    if top['pattern'] in patterns_info:
                        info = patterns_info[top['pattern']]
                        st.write(f"**{info.get('name', '')}**")
                        st.write(info.get('description', ''))
                        
                        with st.expander("Когда использовать"):
                            for w in info.get('when_to_use', []):
                                st.write(f"• {w}")
                        
                        with st.expander("Плюсы / Минусы"):
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.markdown("**Плюсы:**")
                                for p in info.get('pros', []):
                                    st.write(f"✅ {p}")
                            with col_b:
                                st.markdown("**Минусы:**")
                                for c in info.get('cons', []):
                                    st.write(f"❌ {c}")
        
        st.divider()
        
        # === КАЧЕСТВО ===
        st.markdown('<div class="section-header">📊 Оценка качества</div>', 
                    unsafe_allow_html=True)
        
        if r.quality_assessment:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                score = r.quality_assessment.get('overall_score', 0)
                st.metric("Интегральный score", f"{score:.4f}")
                
                # Gauge chart
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Quality Score"},
                    gauge={
                        'axis': {'range': [0, 1]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 0.5], 'color': "lightgray"},
                            {'range': [0.5, 0.8], 'color': "lightyellow"},
                            {'range': [0.8, 1], 'color': "lightgreen"},
                        ],
                    }
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Сценарии
                scenarios = r.quality_assessment.get('scenarios', {})
                if scenarios:
                    df_scenarios = pd.DataFrame([
                        {
                            'Сценарий': s,
                            'P95 (мс)': round(d.get('p95_response_time', 0) * 1000, 1),
                            'Throughput': round(d.get('throughput', 0), 1),
                        }
                        for s, d in scenarios.items()
                    ])
                    st.dataframe(df_scenarios, use_container_width=True)
        
        # === ВРЕМЯ ===
        with st.expander("⏱️ Детали времени выполнения"):
            df_timings = pd.DataFrame([
                {'Этап': k, 'Время (с)': round(v, 2)}
                for k, v in r.timings.items()
            ])
            st.dataframe(df_timings, use_container_width=True)
        
        # === ОШИБКИ ===
        if r.errors:
            st.error(f"⚠️ Ошибок: {len(r.errors)}")
            for err in r.errors:
                st.write(f"• {err}")


# ============================================================
# ВКЛАДКА 3: ТОПОЛОГИЯ
# ============================================================

with tab_topology:
    if 'report' not in st.session_state:
        st.info("👈 Запустите анализ на вкладке «Ввод ТЗ»")
    else:
        rep = st.session_state['report']
        topo = rep.get('topology', {})
        
        if 'error' in topo:
            st.error(f"Ошибка: {topo['error']}")
        else:
            st.markdown('<div class="section-header">🗺️ Граф топологии</div>', 
                        unsafe_allow_html=True)
            
            # Метрики
            metrics = topo.get('metrics', {})
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Узлов", metrics.get('num_nodes', 0))
            with col2:
                st.metric("Рёбер", metrics.get('num_edges', 0))
            with col3:
                st.metric("Плотность", f"{metrics.get('density', 0):.3f}")
            with col4:
                st.metric("Связность", "✅" if metrics.get('is_connected') else "❌")
            
            # Mermaid
            st.subheader("Диаграмма")
            mermaid = topo.get('mermaid', '')
            st.markdown(f"```mermaid\n{mermaid}\n```")
            
            # PNG
            png_path = topo.get('files', {}).get('png')
            if png_path and Path(png_path).exists():
                st.subheader("Визуализация")
                st.image(png_path, use_container_width=True)
            
            # Критические узлы
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("🔥 Критические узлы")
                for node in metrics.get('critical_nodes', []):
                    st.write(f"• `{node['node']}` — degree: {node['degree']}")
            with col2:
                st.subheader("🚧 Узкие места")
                for node in metrics.get('bottlenecks', []):
                    st.write(f"• `{node['node']}` — betweenness: {node['betweenness']}")


# ============================================================
# ВКЛАДКА 4: НАГРУЗКА
# ============================================================

with tab_load:
    if 'report' not in st.session_state:
        st.info("👈 Запустите анализ")
    else:
        rep = st.session_state['report']
        load = rep.get('load', {})
        
        if 'error' in load:
            st.error(f"Ошибка: {load['error']}")
        else:
            st.markdown('<div class="section-header">📈 Входная нагрузка</div>', 
                        unsafe_allow_html=True)
            
            input_load = load.get('input_load', {})
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("I/O точек", input_load.get('io_points', 0))
            with col2:
                st.metric("Событий/сек", f"{input_load.get('events_per_second', 0):,.0f}")
            with col3:
                st.metric("Сеть", f"{input_load.get('bandwidth_mbps', 0)} Mbps")
            with col4:
                st.metric("Данных/год", f"{input_load.get('data_per_year_gb', 0):,.0f} GB")
            
            st.divider()
            
            # Ресурсы
            st.markdown('<div class="section-header">💻 Требуемые ресурсы</div>', 
                        unsafe_allow_html=True)
            
            resources = load.get('resources', {})
            with_reserve = resources.get('with_reserve', {})
            
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("CPU", f"{with_reserve.get('cpu_cores', 0)} cores")
            with col2:
                st.metric("RAM", f"{with_reserve.get('ram_gb', 0)} GB")
            with col3:
                st.metric("Диск/день", f"{with_reserve.get('disk_gb_per_day', 0)} GB")
            with col4:
                st.metric("Диск/год", f"{with_reserve.get('disk_gb_per_year', 0):,.0f} GB")
            with col5:
                st.metric("Сеть", f"{with_reserve.get('network_mbps', 0)} Mbps")
            
            st.divider()
            
            # Нагрузка по компонентам
            st.markdown('<div class="section-header">⚙️ Нагрузка по компонентам</div>', 
                        unsafe_allow_html=True)
            
            per_component = load.get('per_component', [])
            if per_component:
                df_comp = pd.DataFrame([
                    {
                        'Компонент': c['id'],
                        'Тип': c['type'],
                        'Событий/сек': c['events_per_second'],
                        'CPU cores': c['cpu_cores_required'],
                        'RAM (MB)': c['ram_mb'],
                        'Диск/день (GB)': c['disk_gb_per_day'],
                    }
                    for c in per_component
                ])
                st.dataframe(df_comp, use_container_width=True)
                
                # Chart
                fig = px.bar(
                    df_comp,
                    x='Компонент',
                    y='Событий/сек',
                    color='Тип',
                    title='Событий в секунду по компонентам',
                )
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            # Серверы
            st.markdown('<div class="section-header">🖥️ Рекомендуемые серверы</div>', 
                        unsafe_allow_html=True)
            
            servers = resources.get('recommended_servers', [])
            if servers:
                df_srv = pd.DataFrame(servers)
                st.dataframe(df_srv, use_container_width=True)
            
            # Узкие места
            bottlenecks = load.get('bottlenecks', [])
            if bottlenecks:
                st.subheader("🚧 Узкие места")
                for b in bottlenecks:
                    with st.expander(f"{b['component']} ({b['type']})"):
                        st.write(f"**Проблемы:** {', '.join(b['issues'])}")
                        st.json(b['metrics'])
            else:
                st.success("✅ Узких мест не обнаружено")
            
            # Рекомендации
            recommendations = load.get('recommendations', [])
            if recommendations:
                st.subheader("💡 Рекомендации")
                for rec in recommendations:
                    priority_icon = {
                        'high': '🔴',
                        'medium': '🟡',
                        'low': '🟢',
                    }.get(rec['priority'], '⚪')
                    
                    st.write(f"{priority_icon} **{rec['component']}**: {rec['recommendation']}")
                    st.caption(f"Причина: {rec['reason']}")


# ============================================================
# ВКЛАДКА 5: ПЛАН РАБОТ
# ============================================================

with tab_plan:
    if 'report' not in st.session_state:
        st.info("👈 Запустите анализ")
    else:
        rep = st.session_state['report']
        
        # === ПЛАН РАБОТ ===
        st.markdown('<div class="section-header">📅 План работ</div>', 
                    unsafe_allow_html=True)
        
        work_plan = rep.get('work_plan', {})
        if 'error' not in work_plan:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Всего дней", work_plan.get('total_days', 0))
            with col2:
                phases = work_plan.get('phases', [])
                st.metric("Фаз", len(phases))
            
            # Gantt
            if work_plan.get('gantt_mermaid'):
                st.subheader("Gantt")
                st.markdown(f"```mermaid\n{work_plan['gantt_mermaid']}\n```")
            
            # Таблица фаз
            if phases:
                df_phases = pd.DataFrame([
                    {
                        'Фаза': p['name'],
                        'Дней': p['duration_days'],
                        'Роли': ', '.join(p['roles']),
                        'Результат': ', '.join(p['deliverables']),
                    }
                    for p in phases
                ])
                st.dataframe(df_phases, use_container_width=True)
        
        st.divider()
        
        # === ТРУДОЗАТРАТЫ ===
        st.markdown('<div class="section-header">⏱️ Трудозатраты</div>', 
                    unsafe_allow_html=True)
        
        effort = rep.get('effort', {})
        if 'error' not in effort:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Часов", f"{effort.get('total_hours', 0):,}")
            with col2:
                st.metric("Дней", f"{effort.get('total_calendar_days', 0):.0f}")
            with col3:
                st.metric("Чел-мес", effort.get('total_person_months', 0))
            with col4:
                st.metric("Стоимость", f"{effort.get('total_cost_rub', 0):,.0f} ₽")
            
            # По фазам
            by_phase = effort.get('by_phase', [])
            if by_phase:
                df_effort = pd.DataFrame([
                    {'Фаза': p['name'], 'Часы': p['hours']}
                    for p in by_phase
                ])
                fig = px.pie(df_effort, values='Часы', names='Фаза',
                            title='Распределение по фазам')
                st.plotly_chart(fig, use_container_width=True)
            
            # По ролям
            by_role = effort.get('by_role', {})
            if by_role:
                df_roles = pd.DataFrame([
                    {
                        'Роль': role,
                        'Часы': data['hours'],
                        'Ставка': data['rate'],
                        'Стоимость': data['cost'],
                    }
                    for role, data in by_role.items()
                ])
                st.subheader("По ролям")
                st.dataframe(df_roles, use_container_width=True)
            
            # Сравнение
            comparison = effort.get('comparison', {})
            if comparison:
                st.subheader("Сравнение с традиционным подходом")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Традиционно", f"{comparison.get('traditional_hours', 0):,} ч")
                with col2:
                    st.metric("Наш проект", f"{comparison.get('our_hours', 0):,} ч")
                with col3:
                    st.metric("Экономия", f"{comparison.get('savings_percent', 0)}%",
                             delta=f"-{comparison.get('savings_hours', 0)} ч")
        
        st.divider()
        
        # === БЮДЖЕТ ===
        st.markdown('<div class="section-header">💰 Бюджет</div>', 
                    unsafe_allow_html=True)
        
        budget_data = rep.get('budget', {})
        if 'error' not in budget_data:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Pie
                breakdown = budget_data.get('breakdown', {})
                df_budget = pd.DataFrame([
                    {'Статья': k.replace('_percent', ''), 'Процент': v}
                    for k, v in breakdown.items()
                ])
                fig = px.pie(df_budget, values='Процент', names='Статья',
                            title='Структура бюджета')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Метрики
                st.metric("Разработка", f"{budget_data.get('labor_cost_rub', 0):,.0f} ₽")
                st.metric("Оборудование", f"{budget_data.get('equipment_rub', 0):,.0f} ₽")
                st.metric("Лицензии", f"{budget_data.get('licenses_rub', 0):,.0f} ₽")
                st.metric("Обучение", f"{budget_data.get('training_rub', 0):,.0f} ₽")
                st.metric("Резерв (20%)", f"{budget_data.get('reserve_rub', 0):,.0f} ₽")
                st.metric("**ИТОГО**", f"{budget_data.get('total_rub', 0):,.0f} ₽")
        
        st.divider()
        
        # === КОМАНДА ===
        st.markdown('<div class="section-header">👥 Команда</div>', 
                    unsafe_allow_html=True)
        
        team = rep.get('team', {})
        if 'error' not in team:
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Ролей", team.get('total_roles', 0))
            with col2:
                st.metric("FTE", team.get('total_fte', 0))
            
            team_data = team.get('team', [])
            if team_data:
                df_team = pd.DataFrame(team_data)
                st.dataframe(df_team, use_container_width=True)


# ============================================================
# ВКЛАДКА 6: РИСКИ
# ============================================================

with tab_risks:
    if 'report' not in st.session_state:
        st.info("👈 Запустите анализ")
    else:
        rep = st.session_state['report']
        risks = rep.get('risks', {})
        
        if 'error' in risks:
            st.error(f"Ошибка: {risks['error']}")
        else:
            st.markdown('<div class="section-header">⚠️ Риски проекта</div>', 
                        unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Всего рисков", risks.get('total_risks', 0))
            with col2:
                st.metric("Критических", risks.get('critical_count', 0))
            with col3:
                matrix = risks.get('risk_matrix', {})
                st.metric("Высоких", len(matrix.get('high', [])))
            
            st.divider()
            
            # Матрица рисков
            st.subheader("Матрица рисков")
            
            matrix = risks.get('risk_matrix', {})
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("🔴 Critical", len(matrix.get('critical', [])))
            with col2:
                st.metric("🟠 High", len(matrix.get('high', [])))
            with col3:
                st.metric("🟡 Medium", len(matrix.get('medium', [])))
            with col4:
                st.metric("🟢 Low", len(matrix.get('low', [])))
            
            st.divider()
            
            # Список рисков
            st.subheader("Детали рисков")
            
            for risk in risks.get('risks', []):
                icon = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🟢',
                }.get(risk['impact'], '⚪')
                
                with st.expander(f"{icon} [{risk['id']}] {risk['name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Вероятность:** {risk['probability']}")
                        st.write(f"**Влияние:** {risk['impact']}")
                        st.write(f"**Категория:** {risk['category']}")
                    with col2:
                        st.write(f"**Владелец:** {risk['owner']}")
                    
                    st.write(f"**Описание:** {risk['description']}")
                    st.success(f"**Митигация:** {risk['mitigation']}")
            
            st.divider()
            
            # Соответствие стандартам
            st.markdown('<div class="section-header">📋 Соответствие стандартам</div>', 
                        unsafe_allow_html=True)
            
            compliance = rep.get('compliance', {})
            if 'error' not in compliance:
                summary = compliance.get('summary', {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Compliant", summary.get('fully_compliant', 0))
                with col2:
                    st.metric("⚠️ Partial", summary.get('partial', 0))
                with col3:
                    st.metric("❌ Not compliant", summary.get('not_compliant', 0))
                
                # Таблица
                standards = compliance.get('standards', [])
                if standards:
                    df_std = pd.DataFrame([
                        {
                            'Код': s['code'],
                            'Название': s['name'],
                            'Требование': s['requirement'],
                            'Статус': s['status'],
                            'Доказательство': s['evidence'],
                        }
                        for s in standards
                    ])
                    st.dataframe(df_std, use_container_width=True)


# ============================================================
# ВКЛАДКА 7: ЭКСПОРТ
# ============================================================

with tab_export:
    if 'report' not in st.session_state:
        st.info("👈 Запустите анализ")
    else:
        rep = st.session_state['report']
        
        st.markdown('<div class="section-header">💾 Экспорт результатов</div>', 
                    unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📄 Форматы")
            
            # JSON
            json_str = json.dumps(rep, ensure_ascii=False, indent=2, default=str)
            st.download_button(
                "📥 Скачать JSON",
                data=json_str,
                file_name=f"asutp_report_{datetime.now():%Y%m%d_%H%M%S}.json",
                mime="application/json",
                use_container_width=True,
            )
            
            # Markdown
            md_path = Path("results/reports") / f"run_{rep['metadata']['run_name']}" / "REPORT.md"
            if md_path.exists():
                st.download_button(
                    "📥 Скачать Markdown",
                    data=md_path.read_text(encoding='utf-8'),
                    file_name="REPORT.md",
                    mime="text/markdown",
                    use_container_width=True,
                )
            
            # CSV сущностей
            entities = rep.get('entities', [])
            if entities:
                df_entities = pd.DataFrame(entities)
                csv = df_entities.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Скачать сущности (CSV)",
                    data=csv,
                    file_name="entities.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        
        with col2:
            st.subheader("📁 Файлы")
            
            run_name = rep['metadata']['run_name']
            run_dir = Path("results/reports") / f"run_{run_name}"
            
            if run_dir.exists():
                st.write(f"**Директория:** `{run_dir}`")
                
                for f in sorted(run_dir.rglob("*")):
                    if f.is_file():
                        size = f.stat().st_size
                        st.write(f"📄 `{f.relative_to(run_dir)}` ({size:,} B)")
            else:
                st.warning("Директория не найдена")
        
        st.divider()
        
        # === ПОЛНЫЙ JSON ===
        with st.expander("👁️ Просмотр полного JSON"):
            st.json(rep)