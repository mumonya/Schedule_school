# ui.py
from datetime import time
from typing import Tuple, Dict, Any

import pandas as pd
import streamlit as st


def _selectbox_sidebar(label: str, options: list[str], key: str) -> str:
    cur = st.session_state.get(key, options[0])
    idx = options.index(cur) if cur in options else 0
    return st.sidebar.selectbox(label, options, index=idx, key=key)


def render_tab_selector_and_refresh() -> str:
    """
    Верхняя панель: переключатель вкладок + кнопка обновления данных.

    ВАЖНО: тут НЕТ st.rerun().
    Streamlit и так делает rerun при клике на кнопку, поэтому нам достаточно
    очистить cache_data, а дальше код ниже по файлу (app.py) сам загрузит свежие данные
    и применит фильтры в этом же прогоне.
    """
    tabs = ["📅 Расписание", "⚠️ Конфликты"]

    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = tabs[0]
    elif st.session_state["active_tab"] not in tabs:
        st.session_state["active_tab"] = tabs[0]

    col_left, col_right = st.columns([6, 2], vertical_alignment="center")

    with col_left:
        active_tab = st.radio(
            "Вкладка",
            tabs,
            horizontal=True,
            key="active_tab",
            label_visibility="collapsed",
        )

    with col_right:
        if st.button("🔄 Обновить данные", use_container_width=True, key="btn_refresh_data"):
            # Очищаем кэш данных: следующий вызов load_and_process_data() пересчитает все заново
            st.cache_data.clear()
            # Никакого st.rerun() тут не нужно

    return active_tab


# =========================
# ФИЛЬТРЫ РАСПИСАНИЯ (sidebar)
# =========================
def render_filters(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    st.sidebar.header("🔍 Фильтры")

    # День недели
    weekdays = ["Все"] + sorted(
        [str(d).strip() for d in df["День недели"].dropna().unique().tolist() if str(d).strip() != ""]
    )
    selected_weekday = _selectbox_sidebar("День недели:", weekdays, key="f_weekday")

    # Класс
    classes = ["Все"] + sorted(
        [str(c).strip() for c in df["Класс"].dropna().unique().tolist() if str(c).strip() != ""]
    )
    selected_class = _selectbox_sidebar("Класс:", classes, key="f_class")

    # Педагог (точное совпадение)
    teachers = ["Все"] + sorted(
        [str(t).strip() for t in df["Педагог"].dropna().unique().tolist() if str(t).strip() != ""]
    )
    selected_teacher = _selectbox_sidebar("Педагог:", teachers, key="f_teacher")

    # Педагог или тьютор (OR)
    teacher_tutor_people = sorted(
        set(
            [str(x).strip() for x in df["Педагог"].dropna().tolist() if str(x).strip() != ""]
            + [str(x).strip() for x in df["Тьютор"].dropna().tolist() if str(x).strip() != ""]
        )
    )
    selected_teacher_or_tutor = _selectbox_sidebar(
        "Педагог или тьютор:",
        ["Все"] + teacher_tutor_people,
        key="f_teacher_or_tutor",
    )

    # Предмет
    subjects = ["Все"] + sorted(
        [str(s).strip() for s in df["Предмет"].dropna().unique().tolist() if str(s).strip() != ""]
    )
    selected_subject = _selectbox_sidebar("Предмет:", subjects, key="f_subject")

    # Кабинет
    rooms = ["Все"] + sorted(
        [str(r).strip() for r in df["Комната"].dropna().unique().tolist() if str(r).strip() != ""]
    )
    selected_room = _selectbox_sidebar("Кабинет:", rooms, key="f_room")

    # Применение фильтров
    filtered_df = df.copy()

    if selected_weekday != "Все":
        filtered_df = filtered_df[filtered_df["День недели"].astype(str).str.strip() == selected_weekday]

    if selected_class != "Все":
        filtered_df = filtered_df[filtered_df["Класс"].astype(str).str.strip() == selected_class]

    if selected_teacher != "Все":
        filtered_df = filtered_df[filtered_df["Педагог"].astype(str).str.strip() == selected_teacher]

    if selected_teacher_or_tutor != "Все":
        ped = filtered_df["Педагог"].astype(str).str.strip()
        tut = filtered_df["Тьютор"].astype(str).str.strip()
        filtered_df = filtered_df[(ped == selected_teacher_or_tutor) | (tut == selected_teacher_or_tutor)]

    if selected_subject != "Все":
        filtered_df = filtered_df[filtered_df["Предмет"].astype(str).str.strip() == selected_subject]

    if selected_room != "Все":
        filtered_df = filtered_df[filtered_df["Комната"].astype(str).str.strip() == selected_room]

    selected = {
        "weekday": selected_weekday,
        "class": selected_class,
        "teacher": selected_teacher,
        "teacher_or_tutor": selected_teacher_or_tutor,
        "subject": selected_subject,
        "room": selected_room,
    }
    return filtered_df, selected


# =========================
# ФИЛЬТРЫ КОНФЛИКТОВ (sidebar)
# =========================
def render_conflicts_filters(conflicts_df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚠️ Фильтры конфликтов")

    if conflicts_df is None or conflicts_df.empty:
        selected = {"type": "Все", "day": "Все", "q": ""}
        return conflicts_df, selected

    types = ["Все"] + sorted(
        [str(t).strip() for t in conflicts_df["Тип"].dropna().unique().tolist() if str(t).strip() != ""]
    )
    f_type = _selectbox_sidebar("Тип конфликта:", types, key="conf_type")

    days = ["Все"] + sorted(
        [str(d).strip() for d in conflicts_df["День недели"].dropna().unique().tolist() if str(d).strip() != ""]
    )
    f_day = _selectbox_sidebar("День недели:", days, key="conf_day")

    q = st.sidebar.text_input("Поиск (препод/кабинет):", value=st.session_state.get("conf_q", ""), key="conf_q")
    q_norm = str(q).strip().casefold()

    view = conflicts_df.copy()

    if f_type != "Все":
        view = view[view["Тип"].astype(str).str.strip() == f_type]

    if f_day != "Все":
        view = view[view["День недели"].astype(str).str.strip() == f_day]

    if q_norm != "":
        view = view[view["Ресурс"].astype(str).str.casefold().str.contains(q_norm, na=False)]

    selected = {"type": f_type, "day": f_day, "q": q}
    return view, selected


# =========================
# РЕНДЕР ТАБЛИЦ
# =========================
def render_table(filtered_df: pd.DataFrame) -> None:
    st.subheader("📅 Расписание уроков")

    if filtered_df.empty:
        st.info("Нет данных, соответствующих выбранным фильтрам")
        return

    display_df = filtered_df[
        ["День недели", "Номер урока", "Начало", "Конец", "Класс", "Группа",
         "Предмет", "Педагог", "Тьютор", "Комната"]
    ].copy()

    display_df["Начало"] = display_df["Начало"].apply(lambda x: x.strftime("%H:%M") if isinstance(x, time) else "")
    display_df["Конец"] = display_df["Конец"].apply(lambda x: x.strftime("%H:%M") if isinstance(x, time) else "")

    st.dataframe(display_df, use_container_width=True, height=500)
    st.metric("Количество строк (уроков)", len(filtered_df))


def render_diagnostics(meta: Dict[str, Any]) -> None:
    with st.expander("🔧 Диагностика"):
        st.write("Последняя загрузка:", meta.get("last_loaded_at"))
        st.write("Размер сырой таблицы:", meta.get("raw_shape"))
        st.write("Размер обработанной таблицы:", meta.get("processed_shape"))

        if meta.get("warnings"):
            st.warning("\n".join(meta["warnings"]))

        missing_cols = meta.get("missing_columns", [])
        if missing_cols:
            st.write("Отсутствующие ожидаемые колонки (проверь названия в Google Sheet):")
            st.code("\n".join(missing_cols))

        st.write("Колонки, которые реально есть в источнике:")
        st.code(", ".join(meta.get("raw_columns", [])))


def render_footer() -> None:
    st.markdown("---")
    st.subheader("ℹ️ Как использовать")
    st.markdown(
        """
- Нажмите **«Обновить данные»** сверху (рядом с вкладками), чтобы подтянуть свежую таблицу.
- Источник данных: XLSX (локально или по ссылке).
- Для деления на подгруппы используйте переносы строк в **каждой** из колонок (Урок/Педагог/Тьютор/Комната):
  - `A: ...`
  - `B: ...`
- Если, например, **Комната** указана одной строкой без `A:`/`B:`, она будет применена к обеим группам автоматически.
"""
    )


def render_conflicts_tab(conflicts_df: pd.DataFrame, conflicts_meta: Dict[str, Any]) -> None:
    st.subheader("⚠️ Конфликты в расписании")

    if conflicts_df is None or conflicts_df.empty:
        st.success("Конфликтов не найдено ✅")
    else:
        st.error(f"Найдено конфликтов (после фильтров): {len(conflicts_df)}")
        st.dataframe(
            conflicts_df[["Тип", "Ресурс", "День недели", "Пересечение (мин)", "Урок 1", "Урок 2"]],
            use_container_width=True,
            height=550,
        )

    with st.expander("🔎 Диагностика конфликтов"):
        if "error" in conflicts_meta:
            st.error(conflicts_meta["error"])
            return

        st.write("Событий (люди):", conflicts_meta.get("events_person", 0))
        st.write("Событий (кабинеты):", conflicts_meta.get("events_room", 0))
        st.write("Пропущено (нет времени):", conflicts_meta.get("skipped_no_time", 0))
        st.write("Пропущено (нет дня):", conflicts_meta.get("skipped_no_day", 0))
        st.write("Пропущено (нет педагога/тьютора):", conflicts_meta.get("skipped_no_person", 0))
        st.write("Пропущено (нет кабинета):", conflicts_meta.get("skipped_no_room", 0))
