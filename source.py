# source.py
import io
import os
import time as _time
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

import requests
import pandas as pd

from settings import DATA_MODE, LOCAL_XLSX_PATH, XLSX_SHEET_NAME, REMOTE_XLSX_URL
from utils import normalize_columns


def _add_cache_buster(url: str) -> str:
    """
    Добавляет параметр cb=<timestamp_ms> к URL, чтобы обходить кеши (Google/proxy/CDN).
    Работает и для URL с уже существующими query-параметрами.
    """
    parsed = urlparse(url)
    q = dict(parse_qsl(parsed.query, keep_blank_values=True))
    q["cb"] = str(int(_time.time() * 1000))
    new_query = urlencode(q)
    return urlunparse(parsed._replace(query=new_query))


def download_xlsx_bytes(url: str) -> io.BytesIO:
    """
    Скачивает xlsx по URL и возвращает BytesIO.
    Используем cache-buster и no-cache заголовки, чтобы изменения приходили с первого обновления.
    """
    url = _add_cache_buster(url)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return io.BytesIO(resp.content)


def load_raw_table() -> pd.DataFrame:
    """
    Возвращает "сырую" таблицу из источника (XLSX).
    """
    if DATA_MODE == "excel_local":
        if not os.path.exists(LOCAL_XLSX_PATH):
            raise FileNotFoundError(f"Локальный файл не найден: {LOCAL_XLSX_PATH}")
        df = pd.read_excel(LOCAL_XLSX_PATH, sheet_name=XLSX_SHEET_NAME)

    elif DATA_MODE == "excel_url":
        if "PASTE_GOOGLE_EXPORT_XLSX_URL_HERE" in REMOTE_XLSX_URL:
            raise ValueError("Вставь реальный REMOTE_XLSX_URL.")
        bio = download_xlsx_bytes(REMOTE_XLSX_URL)
        df = pd.read_excel(bio, sheet_name=XLSX_SHEET_NAME)

    else:
        raise ValueError("DATA_MODE должен быть 'excel_local' или 'excel_url'.")

    return normalize_columns(df)
