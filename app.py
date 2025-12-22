# app.py
import streamlit as st

from settings import DATA_MODE
from transform import load_and_process_data
from conflicts import detect_conflicts
from ui import (
    render_tab_selector_and_refresh,
    render_filters,                # фильтры расписания (sidebar)
    render_conflicts_filters,      # фильтры конфликтов (sidebar)
    render_table,
    render_diagnostics,
    render_footer,
    render_conflicts_tab,
)

st.set_page_config(page_title="Школьное расписание", page_icon="📚", layout="wide")
st.title("📚 Цифровое школьное расписание")
st.markdown("---")

# Вкладки + кнопка обновления (кнопка теперь просто чистит cache_data)
active_tab = render_tab_selector_and_refresh()

# ===== загрузка данных (ОДИН РАЗ) =====
try:
    df, meta = load_and_process_data()
    meta["source_mode"] = DATA_MODE
except Exception as e:
    st.error(f"Ошибка загрузки данных: {e}")
    st.stop()

if df.empty:
    st.warning(
        "Данные загрузились, но итоговое расписание пустое "
        "(проверь типы 'урок/перемена' и названия колонок)."
    )
    st.stop()

# ===== конфликты =====
conflicts_df, conflicts_meta = detect_conflicts(df)

# ===== рендер активной вкладки =====
if active_tab == "📅 Расписание":
    filtered_schedule_df, _ = render_filters(df)
    render_table(filtered_schedule_df)
    render_diagnostics(meta)
    render_footer()
else:
    filtered_conflicts_df, _ = render_conflicts_filters(conflicts_df)
    render_conflicts_tab(filtered_conflicts_df, conflicts_meta)
