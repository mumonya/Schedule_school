# app.py
import streamlit as st

from settings import DATA_MODE
from transform import load_and_process_data
from conflicts import detect_conflicts
from ui import (
    inject_auto_refresh,
    manual_refresh_button,
    render_filters,
    render_table,
    render_diagnostics,
    render_footer,
    render_conflicts_tab,
)

# =========================
# UI: страница
# =========================
st.set_page_config(page_title="Школьное расписание", page_icon="📚", layout="wide")
st.title("📚 Цифровое школьное расписание")
st.markdown("---")

# Авто-обновление + ручное обновление
inject_auto_refresh()
manual_refresh_button()

# =========================
# Основная загрузка
# =========================
try:
    df, meta = load_and_process_data()
    meta["source_mode"] = DATA_MODE
except Exception as e:
    st.error(f"Ошибка загрузки данных: {e}")
    st.stop()

if df.empty:
    st.warning("Данные загрузились, но итоговое расписание пустое (проверь типы 'урок/перемена' и названия колонок).")
    st.stop()

# =========================
# Конфликты (на основе уже готового df)
# =========================
conflicts_df, conflicts_meta = detect_conflicts(df)

# =========================
# Вкладки
# =========================
tab_schedule, tab_conflicts = st.tabs(["📅 Расписание", "⚠️ Конфликты"])

with tab_schedule:
    filtered_df, _selected = render_filters(df)
    render_table(filtered_df)
    render_diagnostics(meta)
    render_footer()

with tab_conflicts:
    render_conflicts_tab(conflicts_df, conflicts_meta)
