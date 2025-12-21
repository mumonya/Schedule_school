# utils.py
from datetime import datetime, time
from typing import Any, Optional, List

import pandas as pd


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Приводим названия колонок к стабильному виду:
    - меняем неразрывные пробелы на обычные
    - схлопываем многопробельные последовательности
    - обрезаем пробелы по краям
    """
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.replace("\u00A0", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    return df


def to_time(val: Any) -> Optional[time]:
    """
    Приводит значение из Excel к datetime.time.
    Поддерживает:
    - datetime / pandas Timestamp
    - time
    - строки '08:30' / '08:30:00'
    """
    if val is None or (isinstance(val, float) and pd.isna(val)) or (isinstance(val, str) and val.strip() == ""):
        return None

    if hasattr(val, "to_pydatetime"):
        val = val.to_pydatetime()

    if isinstance(val, datetime):
        return val.time()

    if isinstance(val, time):
        return val

    if isinstance(val, str):
        s = val.strip()
        for fmt in ("%H:%M", "%H:%M:%S"):
            try:
                return datetime.strptime(s, fmt).time()
            except ValueError:
                pass

    return None


def safe_str(val: Any) -> str:
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    return str(val).strip()


def split_lines(cell: str) -> List[str]:
    """
    Делит содержимое ячейки по переносам строк (Alt+Enter).
    """
    cell = cell.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.strip() for ln in cell.split("\n")]
    return [ln for ln in lines if ln != ""]
