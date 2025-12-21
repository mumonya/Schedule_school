# ui.py
from datetime import time
from typing import Tuple, Dict, Any

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from settings import REFRESH_EVERY_SECONDS


def inject_auto_refresh() -> None:
    components.html(
        f"""
        <script>
          setTimeout(function() {{
            window.location.reload();
          }}, {REFRESH_EVERY_SECONDS * 1000});
        </script>
        """,
        height=0
    )


def manual_refresh_button() -> None:
    if st.sidebar.button("🔄 Обновить сейчас"):
        st.cache_data.clear()
        st.rerun()


def render_filters(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, str]]:
    st.sidebar.header("🔍 Фильтры")

    # ✅ Новый фильтр: день недели (вместо группы)
    weekdays = ["Все"] + sorted([d for d in df["День недели"].dropna().unique().tolist() if str(d).strip() != ""])
    selected_weekday = st.sidebar.selectbox("Выберите день недели:", weekdays)

    classes = ["Все"] + sorted(df["Класс"].dropna().unique().tolist())
    selected_class = st.sidebar.selectbox("Выберите класс:", classes)

    teachers = ["Все"] + sorted([t for t in df["Педагог"].dropna().unique().tolist() if str(t).strip() != ""])
    selected_teacher = st.sidebar.selectbox("Выберите педагога:", teachers)

    teacher_tutor_people = sorted(set(
        [x for x in df["Педагог"].dropna().tolist() if str(x).strip() != ""] +
        [x for x in df["Тьютор"].dropna().tolist() if str(x).strip() != ""]
    ))
    selected_teacher_or_tutor = st.sidebar.selectbox(
        "Педагог или тьютор:",
        ["Все"] + teacher_tutor_people
    )

    subjects = ["Все"] + sorted([s for s in df["Предмет"].dropna().unique().tolist() if str(s).strip() != ""])
    selected_subject = st.sidebar.selectbox("Выберите предмет:", subjects)

    rooms = ["Все"] + sorted([r for r in df["Комната"].dropna().unique().tolist() if str(r).strip() != ""])
    selected_room = st.sidebar.selectbox("Выберите кабинет:", rooms)

    filtered_df = df.copy()

    if selected_weekday != "Все":
        filtered_df = filtered_df[filtered_df["День недели"] == selected_weekday]

    if selected_class != "Все":
        filtered_df = filtered_df[filtered_df["Класс"] == selected_class]

    if selected_teacher != "Все":
        filtered_df = filtered_df[filtered_df["Педагог"] == selected_teacher]

    if selected_teacher_or_tutor != "Все":
        filtered_df = filtered_df[
            (filtered_df["Педагог"] == selected_teacher_or_tutor) |
            (filtered_df["Тьютор"] == selected_teacher_or_tutor)
        ]

    if selected_subject != "Все":
        filtered_df = filtered_df[filtered_df["Предмет"] == selected_subject]

    if selected_room != "Все":
        filtered_df = filtered_df[filtered_df["Комната"] == selected_room]

    selected = {
        "weekday": selected_weekday,
        "class": selected_class,
        "teacher": selected_teacher,
        "teacher_or_tutor": selected_teacher_or_tutor,
        "subject": selected_subject,
        "room": selected_room,
    }
    return filtered_df, selected


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
- Данные автоматически обновляются раз в 10 минут (страница перезагружается).
- Можно нажать **«Обновить сейчас»** в боковой панели.
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
        st.error(f"Найдено конфликтов: {len(conflicts_df)}")

        # Фильтры внутри вкладки (не в sidebar, чтобы не мешать расписанию)
        col_a, col_b, col_c = st.columns([1, 1, 2])

        with col_a:
            types = ["Все"] + sorted([t for t in conflicts_df["Тип"].dropna().unique().tolist() if str(t).strip() != ""])
            f_type = st.selectbox("Тип конфликта:", types, key="conf_type")

        with col_b:
            days = ["Все"] + sorted([d for d in conflicts_df["День недели"].dropna().unique().tolist() if str(d).strip() != ""])
            f_day = st.selectbox("День недели:", days, key="conf_day")

        with col_c:
            q = st.text_input("Поиск по ресурсу (препод/кабинет):", value="", key="conf_q").strip().casefold()

        view = conflicts_df.copy()
        if f_type != "Все":
            view = view[view["Тип"] == f_type]
        if f_day != "Все":
            view = view[view["День недели"] == f_day]
        if q != "":
            view = view[view["Ресурс"].astype(str).str.casefold().str.contains(q, na=False)]

        st.dataframe(
            view[["Тип", "Ресурс", "День недели", "Пересечение (мин)", "Урок 1", "Урок 2"]],
            use_container_width=True,
            height=550
        )

    # Небольшая диагностика по конфликтам (почему что-то могло не провериться)
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