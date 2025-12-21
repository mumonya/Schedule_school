# conflicts.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd


def _norm_key(s: str) -> str:
    # Нормализуем, чтобы "Иванова", "иванова " считались одним человеком
    return " ".join(str(s).strip().split()).casefold()


def _time_to_min(t: time) -> int:
    return t.hour * 60 + t.minute


def _overlap_minutes(a_start: int, a_end: int, b_start: int, b_end: int) -> int:
    # Пересечение интервалов (в минутах). Если касаются краями — 0.
    left = max(a_start, b_start)
    right = min(a_end, b_end)
    return max(0, right - left)


def _fmt_time(t: Optional[time]) -> str:
    return t.strftime("%H:%M") if isinstance(t, time) else ""


def _lesson_brief(row: Dict[str, Any]) -> str:
    # Короткое описание урока для таблички конфликтов
    grp = row.get("Группа", "")
    grp_part = f" [{grp}]" if str(grp).strip() != "" else ""
    return (
        f"{row.get('Класс','')}{grp_part}: {row.get('Предмет','')}; "
        f"{_fmt_time(row.get('Начало'))}-{_fmt_time(row.get('Конец'))}; "
        f"каб. {row.get('Комната','')}; "
        f"пед. {row.get('Педагог','')}; тьют. {row.get('Тьютор','')}"
    )


@dataclass
class _Event:
    resource_type: str        # "person" или "room"
    resource_key: str         # нормализованный ключ
    resource_label: str       # как показать пользователю
    day: str
    start: time
    end: time
    start_min: int
    end_min: int
    lesson: Dict[str, Any]    # данные строки расписания (для вывода)


def build_events(df: pd.DataFrame) -> Tuple[List[_Event], Dict[str, Any]]:
    """
    Превращаем расписание в список "событий" для проверки конфликтов.
    Для людей: берём и Педагога, и Тьютора (оба считаются одним типом ресурса: person).
    Для кабинетов: берём Комнату.
    """
    meta = {
        "skipped_no_time": 0,
        "skipped_no_day": 0,
        "skipped_no_person": 0,
        "skipped_no_room": 0,
        "events_person": 0,
        "events_room": 0,
    }

    events: List[_Event] = []

    required_cols = ["День недели", "Начало", "Конец", "Класс", "Группа", "Предмет", "Педагог", "Тьютор", "Комната"]
    # если каких-то колонок нет — просто вернем пусто, а диагностика покажет проблему в исходном блоке
    for c in required_cols:
        if c not in df.columns:
            return [], {"error": f"В df нет колонки '{c}'"}

    for _, r in df.iterrows():
        day = str(r.get("День недели", "")).strip()
        if day == "":
            meta["skipped_no_day"] += 1
            continue

        start = r.get("Начало", None)
        end = r.get("Конец", None)
        if not isinstance(start, time) or not isinstance(end, time):
            meta["skipped_no_time"] += 1
            continue

        smin = _time_to_min(start)
        emin = _time_to_min(end)
        if emin <= smin:
            # на всякий случай: неправильный интервал времени
            meta["skipped_no_time"] += 1
            continue

        row_dict = {
            "День недели": day,
            "Начало": start,
            "Конец": end,
            "Класс": str(r.get("Класс", "")).strip(),
            "Группа": str(r.get("Группа", "")).strip(),
            "Предмет": str(r.get("Предмет", "")).strip(),
            "Педагог": str(r.get("Педагог", "")).strip(),
            "Тьютор": str(r.get("Тьютор", "")).strip(),
            "Комната": str(r.get("Комната", "")).strip(),
        }

        # --- Люди (педагог + тьютор)
        people = []
        if row_dict["Педагог"] != "":
            people.append(row_dict["Педагог"])
        if row_dict["Тьютор"] != "" and row_dict["Тьютор"] != row_dict["Педагог"]:
            people.append(row_dict["Тьютор"])

        if not people:
            meta["skipped_no_person"] += 1
        else:
            for p in people:
                events.append(
                    _Event(
                        resource_type="person",
                        resource_key=_norm_key(p),
                        resource_label=p,
                        day=day,
                        start=start,
                        end=end,
                        start_min=smin,
                        end_min=emin,
                        lesson=row_dict,
                    )
                )
                meta["events_person"] += 1

        # --- Кабинеты
        room = row_dict["Комната"]
        if room == "":
            meta["skipped_no_room"] += 1
        else:
            events.append(
                _Event(
                    resource_type="room",
                    resource_key=_norm_key(room),
                    resource_label=room,
                    day=day,
                    start=start,
                    end=end,
                    start_min=smin,
                    end_min=emin,
                    lesson=row_dict,
                )
            )
            meta["events_room"] += 1

    return events, meta


def detect_conflicts(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Возвращает:
      - conflicts_df: строки конфликтов
      - meta: статистика (сколько событий, сколько пропусков, и т.п.)
    """
    events, meta = build_events(df)
    if not events:
        meta["conflicts_found"] = 0
        return pd.DataFrame(), meta

    # Группируем по (тип ресурса, день, ресурс)
    buckets: Dict[Tuple[str, str, str], List[_Event]] = {}
    for ev in events:
        key = (ev.resource_type, ev.day, ev.resource_key)
        buckets.setdefault(key, []).append(ev)

    conflicts_rows: List[Dict[str, Any]] = []

    for (rtype, day, rkey), evs in buckets.items():
        # сортируем по началу
        evs_sorted = sorted(evs, key=lambda e: e.start_min)

        active: List[_Event] = []  # события, которые еще не закончились
        for cur in evs_sorted:
            # выкидываем завершившиеся к моменту начала текущего
            active = [a for a in active if a.end_min > cur.start_min]

            # проверяем пересечения с активными
            for a in active:
                ov = _overlap_minutes(a.start_min, a.end_min, cur.start_min, cur.end_min)
                if ov > 0:
                    conflicts_rows.append({
                        "Тип": "Преподаватель/тьютор" if rtype == "person" else "Кабинет",
                        "Ресурс": cur.resource_label if rtype != "person" else (cur.resource_label or a.resource_label),
                        "День недели": day,
                        "Пересечение (мин)": ov,
                        "Урок 1": _lesson_brief(a.lesson),
                        "Урок 2": _lesson_brief(cur.lesson),
                        "__sort_rtype": 0 if rtype == "person" else 1,
                        "__sort_key": rkey,
                    })

            active.append(cur)

    conflicts_df = pd.DataFrame(conflicts_rows)

    if not conflicts_df.empty:
        # сортировка: сначала люди, потом кабинеты; затем день; затем величина пересечения
        day_order = {"Понедельник": 1, "Вторник": 2, "Среда": 3, "Четверг": 4, "Пятница": 5}
        conflicts_df["__day_order"] = conflicts_df["День недели"].map(day_order).fillna(99).astype(int)
        conflicts_df = conflicts_df.sort_values(
            ["__sort_rtype", "__day_order", "Пересечение (мин)"],
            ascending=[True, True, False],
        ).drop(columns=["__sort_rtype", "__sort_key", "__day_order"])

    meta["conflicts_found"] = int(len(conflicts_df))
    return conflicts_df, meta
