# transform.py
from datetime import datetime
from typing import Dict, Any, Optional, Tuple

import pandas as pd
import streamlit as st

from settings import REFRESH_EVERY_SECONDS, WEEKDAY_MAP, CLASS_CONFIGS
from source import load_raw_table
from utils import safe_str, to_time
from groups import parse_grouped_field, collect_groups, value_for_group


def detect_missing_columns(df: pd.DataFrame) -> list[str]:
    required = [
        "ДН",
        "Тип началка", "Тип старшая",
        "Начало началка", "Конец началка",
        "Начало старшая", "Конец старшая",
        "Номер слота", "Номер старшая"
    ]
    for cfg in CLASS_CONFIGS.values():
        required += [cfg["subject_col"], cfg["teacher_col"], cfg["tutor_col"], cfg["room_col"]]
    return [c for c in required if c not in df.columns]


def get_timeslot(row: pd.Series, level: str) -> Tuple[Optional[int], Optional[object], Optional[object], Optional[str]]:
    if level == "primary":
        lesson_type = safe_str(row.get("Тип началка")).lower() or None
        num = row.get("Номер слота")
        start = to_time(row.get("Начало началка"))
        end = to_time(row.get("Конец началка"))
    else:
        lesson_type = safe_str(row.get("Тип старшая")).lower() or None
        num = row.get("Номер старшая")
        start = to_time(row.get("Начало старшая"))
        end = to_time(row.get("Конец старшая"))

    try:
        num_int = int(float(num)) if num is not None and str(num).strip() != "" else None
    except Exception:
        num_int = None

    return num_int, start, end, lesson_type


@st.cache_data(ttl=REFRESH_EVERY_SECONDS)
def load_and_process_data() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    meta: Dict[str, Any] = {"warnings": [], "missing_columns": []}

    df_raw = load_raw_table()
    meta["raw_shape"] = df_raw.shape
    meta["raw_columns"] = df_raw.columns.tolist()

    missing = detect_missing_columns(df_raw)
    meta["missing_columns"] = missing
    if missing:
        meta["warnings"].append(
            "В таблице не найдены некоторые ожидаемые колонки. Часть данных может не отобразиться корректно."
        )

    processed_rows = []

    for _, row in df_raw.iterrows():
        day_abbr = safe_str(row.get("ДН"))
        if day_abbr == "":
            continue

        day_full = WEEKDAY_MAP.get(day_abbr, day_abbr)

        for class_name, cfg in CLASS_CONFIGS.items():
            num, start, end, lesson_type = get_timeslot(row, cfg["level"])
            if lesson_type != "урок":
                continue

            subject_map = parse_grouped_field(row.get(cfg["subject_col"]))
            if not subject_map:
                continue

            teacher_map = parse_grouped_field(row.get(cfg["teacher_col"]))
            tutor_map = parse_grouped_field(row.get(cfg["tutor_col"]))
            room_map = parse_grouped_field(row.get(cfg["room_col"]))

            groups = collect_groups(subject_map, teacher_map, tutor_map, room_map)

            for grp in groups:
                subject = value_for_group(subject_map, grp).strip()
                if subject == "":
                    continue

                processed_rows.append({
                    "День недели": day_full,
                    "Номер урока": num,
                    "Начало": start,
                    "Конец": end,
                    "Класс": class_name,
                    "Группа": "" if grp == "All" else grp,
                    "Предмет": subject,
                    "Педагог": value_for_group(teacher_map, grp).strip(),
                    "Тьютор": value_for_group(tutor_map, grp).strip(),
                    "Комната": value_for_group(room_map, grp).strip(),
                })

    result_df = pd.DataFrame(processed_rows)

    if not result_df.empty:
        day_order = {"Понедельник": 1, "Вторник": 2, "Среда": 3, "Четверг": 4, "Пятница": 5}
        result_df["__day_order"] = result_df["День недели"].map(day_order).fillna(99).astype(int)
        result_df = result_df.sort_values(["__day_order", "Номер урока", "Класс", "Группа"]).drop(columns="__day_order")

    meta["processed_shape"] = result_df.shape
    meta["last_loaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return result_df, meta
