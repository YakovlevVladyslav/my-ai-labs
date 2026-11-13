"""Streamlit UI: run with `streamlit run app.py`."""
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from fuzzy_model import LABELS, RULES, TERM_LABELS
from inference import infer
from recommendations import get_recommendations
from visualization import plot_aggregation, plot_membership

st.set_page_config(page_title="AI Lab 4 — Состояние сети", page_icon="🌐", layout="wide")
st.title("Лабораторная №4 · Нечёткая система Мамдани")
st.caption("Вариант 7 — оценка состояния компьютерной сети")

with st.form("inputs"):
    col1, col2, col3 = st.columns(3)
    with col1:
        load = st.number_input("Загрузка канала (%)", min_value=0.0, max_value=100.0, value=65.0, step=1.0)
    with col2:
        latency = st.number_input("Задержка RTT (мс)", min_value=0.0, max_value=300.0, value=150.0, step=1.0)
    with col3:
        errors = st.number_input("Доля ошибок (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1)
    calculate = st.form_submit_button("Рассчитать состояние сети", type="primary", use_container_width=True)

if calculate:
    try:
        st.session_state.result = infer(load, latency, errors)
    except ValueError as exc:
        st.error(str(exc))
        st.session_state.pop("result", None)

result = st.session_state.get("result")
if result is None:
    st.info("Введите значения и нажмите «Рассчитать состояние сети».")
    st.stop()

# Show the input values actually used for the displayed result, even if the form was edited without submitting.
a, b = st.columns([1, 2])
with a:
    st.metric("Оценка", f"{result.score:.2f} / 100")
    st.subheader(result.label)
    st.caption("Вход расчёта: " + ", ".join(f"{LABELS[key][0]} = {value:g} {LABELS[key][1]}" for key, value in result.inputs.items()))
with b:
    st.markdown("**Рекомендации**")
    for recommendation in get_recommendations(result):
        st.write("• " + recommendation)

first, second, third = st.tabs(["Фаззификация", "Правила IF–THEN", "Агрегация и центроид"])
with first:
    cols = st.columns(2)
    for i, variable in enumerate(("load", "latency", "errors", "state")):
        value = result.inputs.get(variable)
        with cols[i % 2]:
            fig = plot_membership(variable, value)
            st.pyplot(fig)
            plt.close(fig)
            if value is not None:
                st.dataframe(pd.DataFrame([
                    {"Терм": TERM_LABELS[variable][term], "Принадлежность": round(degree, 4)}
                    for term, degree in result.memberships[variable].items()
                ]), hide_index=True, use_container_width=True)
with second:
    st.markdown("Для AND используется минимум; для OR — максимум. Все правила вычисляются при каждом расчёте.")
    st.dataframe(pd.DataFrame([
        {"Правило": rule.code, "Условие → результат": rule.description,
         "Сила активации": round(result.activations[rule.code], 4),
         "Вывод": TERM_LABELS["state"][rule.output]}
        for rule in RULES
    ]), use_container_width=True, hide_index=True)
with third:
    st.markdown("Для каждого правила функция выхода обрезается оператором `min(активация, μ_выхода)`. Затем результаты объединяются через `max`, и вычисляется центроид площади.")
    fig = plot_aggregation(result)
    st.pyplot(fig)
    plt.close(fig)
    st.latex(r"y^*=\frac{\int_0^{100} y\,\mu_{aggregated}(y)\,dy}{\int_0^{100}\mu_{aggregated}(y)\,dy}")
    st.write(f"Итог: **{result.score:.2f} / 100** — **{result.label.lower()}** состояние сети.")
