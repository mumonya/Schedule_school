# settings.py

# Режим источника данных:
# - "excel_local" для локальной отладки (чтение xlsx с диска)
# - "excel_url" для прод-режима (скачивание xlsx по ссылке из Google Sheets export)
DATA_MODE = "excel_url"

# Локальный Excel (для отладки)
LOCAL_XLSX_PATH = r"D:\Schedule_mom\Application_fin\Расписание 2025.xlsx"
XLSX_SHEET_NAME = "Расписание"

# Ссылка на XLSX (Google Sheets export / publish xlsx)
REMOTE_XLSX_URL = (
    "https://docs.google.com/spreadsheets/d/e/2PACX-1vSq2NeYnCuzHMDOezQKC5z4qkox9cuGFzxz1sZS7MkVw31Y0Z8Xm2xcKYUCM6_2sFFD75dadertqbZI/pub?output=xlsx"
)

# Авто-обновление (секунды)
REFRESH_EVERY_SECONDS = 600  # 10 минут


WEEKDAY_MAP = {
    "ПНД": "Понедельник",
    "ВТР": "Вторник",
    "СР": "Среда",
    "ЧТ": "Четверг",
    "ПТЦ": "Пятница",
}

CLASS_CONFIGS = {
    "Старт": {"level": "primary", "subject_col": "Старт Урок", "teacher_col": "Старт Педагог", "tutor_col": "Старт Тьютор", "room_col": "Старт Комната"},
    "1 класс": {"level": "primary", "subject_col": "1 класс Урок", "teacher_col": "1 класс Педагог", "tutor_col": "1 класс Тьютор", "room_col": "1 класс Комната"},
    "2 класс": {"level": "primary", "subject_col": "2 класс Урок", "teacher_col": "2 класс Педагог", "tutor_col": "2 класс Тьютор", "room_col": "2 класс Комната"},
    "3 класс": {"level": "primary", "subject_col": "3 класс Урок", "teacher_col": "3 класс Педагог", "tutor_col": "3 класс Тьютор", "room_col": "3 класс Комната"},
    "4 класс": {"level": "primary", "subject_col": "4 класс Урок", "teacher_col": "4 класс Педагог", "tutor_col": "4 класс Тьютор", "room_col": "4 класс Комната"},
    "5 класс": {"level": "secondary", "subject_col": "5 класс Урок", "teacher_col": "5 класс Педагог", "tutor_col": "5 класс Тьютор", "room_col": "5 класс Комната"},
    "6 класс": {"level": "secondary", "subject_col": "6 класс Урок", "teacher_col": "6 класс Педагог", "tutor_col": "6 класс Тьютор", "room_col": "6 класс Комната"},
    "7 класс": {"level": "secondary", "subject_col": "7 класс Урок", "teacher_col": "7 класс Педагог", "tutor_col": "7 класс Тьютор", "room_col": "7 класс Комната"},
    "8 класс": {"level": "secondary", "subject_col": "8 класс Урок", "teacher_col": "8 класс Педагог", "tutor_col": "8 класс Тьютор", "room_col": "8 класс Комната"},
    "9 класс": {"level": "secondary", "subject_col": "9 класс Урок", "teacher_col": "9 класс Педагог", "tutor_col": "9 класс Тьютор", "room_col": "9 класс Комната"},
}
