import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

from main_body import generate_financials, enrich_financials

# --- 1. Генерація або завантаження БД ---
st.set_page_config(page_title="Аналіз фінансових показників", layout="wide")

st.title("📊 Інтерактивний аналіз фінансових показників")

if st.button("🔁 Створити нову базу даних"):
    df = generate_financials()
    st.success("✅ Нову базу даних створено!")
else:
    df = pd.read_csv("financials.csv")

df = enrich_financials(df)

# --- 2. Панель управління ---
col1, col2, col3 = st.columns(3)
years = sorted(df["Year"].unique())
industries = df["Industry"].unique()
companies = df["Company"].unique()

selected_years = col1.slider("📅 Обери роки", int(min(years)), int(max(years)), (2010, 2023))
selected_industries = col2.multiselect("🏭 Обери галузі", industries, default=list(industries))
selected_metric = col3.selectbox(
    "📈 Обери показник для графіка:",
    ["NetMargin", "GrossMargin", "OperatingMargin", "ROA", "ROE"]
)

# --- 3. Фільтрація даних ---
df_filtered = df[
    (df["Year"] >= selected_years[0]) &
    (df["Year"] <= selected_years[1]) &
    (df["Industry"].isin(selected_industries))
]

# --- 4. Побудова графіка ---
fig = px.line(
    df_filtered,
    x="Year",
    y=selected_metric,
    color="Company",
    markers=True,
    title=f"{selected_metric} з {selected_years[0]} по {selected_years[1]}"
)

# Додаткові кнопки керування (масштаб, панорама, ресет)
fig.update_layout(
    hovermode="x unified",
    xaxis=dict(
        rangeslider=dict(visible=True),
        showspikes=True,
        spikemode="across",
        spikecolor="gray"
    ),
    yaxis_tickformat=".2%",
    legend_title_text="Компанія",
)

# --- 5. Відображення графіка та таблиці ---
st.plotly_chart(fig, use_container_width=True)

# --- 6. Таблиця даних ---
st.dataframe(df_filtered.round(2), use_container_width=True)