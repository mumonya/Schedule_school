# groups.py
import re
from typing import Dict, Any, List

from utils import safe_str, split_lines

# допускаем пустое значение после двоеточия: "B:" -> {"B":""}
GROUP_LINE_RE = re.compile(r"^\s*([^:]+)\s*:\s*(.*)\s*$")


def parse_grouped_field(cell_value: Any) -> Dict[str, str]:
    """
    Парсит ячейку:
    - обычная: "История" -> {"All": "История"}
    - групповая:
        "A: Алгебра\nB: Геометрия" -> {"A":"Алгебра", "B":"Геометрия"}
      поддерживает пустые значения:
        "B:" -> {"B":""}
    """
    s = safe_str(cell_value)
    if s == "":
        return {}

    lines = split_lines(s)
    has_group_markup = any(GROUP_LINE_RE.match(ln) for ln in lines)

    if not has_group_markup:
        return {"All": s}

    out: Dict[str, str] = {}
    for ln in lines:
        m = GROUP_LINE_RE.match(ln)
        if m:
            grp = m.group(1).strip()
            val = m.group(2).strip()
            out[grp] = val
        else:
            out.setdefault("All", "")
            out["All"] = (out["All"] + " " + ln).strip()

    return out


def collect_groups(*maps: Dict[str, str]) -> List[str]:
    """
    Собирает список групп (A/B/...) как объединение ключей из всех карт,
    кроме "All". Если групп нет — возвращаем ["All"] (обычный урок).
    """
    groups = set()
    for m in maps:
        for k in m.keys():
            if k != "All":
                groups.add(k)
    if not groups:
        return ["All"]
    return sorted(groups)


def value_for_group(m: Dict[str, str], group: str) -> str:
    """
    Возвращает значение для группы:
    - сначала пробуем конкретную группу (A/B/...)
    - если нет — берём All (одно значение на всех)
    - иначе пусто
    """
    if group in m:
        return m[group]
    return m.get("All", "")
