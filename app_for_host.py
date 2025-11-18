import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Настройка страницы
st.set_page_config(
    page_title="Школьное расписание",
    page_icon="📚",
    layout="wide"
)

# Заголовок приложения
st.title("📚 Цифровое школьное расписание")
st.markdown("---")


def load_data():
    """
    Локальная загрузка файла расписания с ноута.
    Ожидается файл 'Расписание 2025.xlsx' в текущей папке
    или в папке data/.
    """
    filename = "Расписание 2025.xlsx"

    possible_paths = [
        filename,
        f"./{filename}",
        os.path.join("data", filename),
    ]



    for path in possible_paths:
        if os.path.exists(path):
            # В новом файле лист называется "Расписание"
            return pd.read_excel(path, sheet_name="Расписание")

    st.error(f"Файл с расписанием '{filename}' не найден")
    return None


@st.cache_data
def load_and_process_data():
    try:
        df = load_data()
        if df is None:
            return pd.DataFrame()

        # Мэппинг сокращений дней в полные названия
        weekday_map = {
            "ПНД": "Понедельник",
            "ВТР": "Вторник",
            "СР": "Среда",
            "ЧТ": "Четверг",
            "ПТЦ": "Пятница",
        }

        # Настройки по каждому классу:
        # указано, какую временную сетку использовать и какие колонки читать
        class_configs = {
            "Старт": {
                "level": "primary",
                "subject_col": "Старт Урок",
                "teacher_col": "Старт Педагог",
                "tutor_col": "Старт Тьютор",
                "room_col": "Старт Комната",
            },
            "1 класс": {
                "level": "primary",
                "subject_col": "1 класс Урок",
                "teacher_col": "1 класс Педагог",
                "tutor_col": "1 класс Тьютор",
                "room_col": "1 класс Комната",
            },
            "2 класс": {
                "level": "primary",
                "subject_col": "2 класс Урок",
                "teacher_col": "2 класс Педагог",
                "tutor_col": "2 класс Тьютор",
                "room_col": "2  класс Комната",
            },
            "3 класс": {
                "level": "primary",
                "subject_col": "3 класс Урок",
                "teacher_col": "3 класс Педагог",
                "tutor_col": "3 класс Тьютор",
                "room_col": "3 класс Комната",
            },
            "4 класс": {
                "level": "primary",
                "subject_col": "4 класс Урок",
                "teacher_col": "4 класс Педагог",
                "tutor_col": "4 класс Тьютор",
                "room_col": "4 класс Комната",
            },
            "5 класс": {
                "level": "secondary",
                "subject_col": "5 класс Урок",
                "teacher_col": "5 класс Педагог",
                "tutor_col": "5 класс Тьютор",
                "room_col": "5 класс Комната",
            },
            "6 класс": {
                "level": "secondary",
                "subject_col": "6 класс Урок",
                "teacher_col": "6 класс Педагог",
                "tutor_col": "6 класс Тьютор",
                "room_col": "6 класс Комната",
            },
            "7 класс": {
                "level": "secondary",
                "subject_col": "7 класс Урок",
                "teacher_col": "7 класс Педагог",
                "tutor_col": "7 класс Тьютор",
                "room_col": "7 класс Комната",
            },
            "8 класс": {
                "level": "secondary",
                "subject_col": "8 класс Урок",
                "teacher_col": "8 класс Педагог",
                "tutor_col": "8 класс Тьютор",
                "room_col": "8 класс Комната",
            },
            "9 класс": {
                "level": "secondary",
                "subject_col": "9 класс Урок",
                "teacher_col": "9  класс Педагог",
                "tutor_col": "9 класс Тьютор",
                "room_col": "9 класс Комната",
            },
        }

        processed_data = []

        for idx, row in df.iterrows():
            day_abbr = row.get("ДН")
            if pd.isna(day_abbr):
                continue

            day_full = weekday_map.get(str(day_abbr).strip(), str(day_abbr).strip())

            for class_name, cfg in class_configs.items():
                subject = row.get(cfg["subject_col"])

                # если предмет пустой — пропускаем
                if pd.isna(subject) or str(subject).strip() == "":
                    continue

                # Выбираем правильную временную сетку
                if cfg["level"] == "primary":
                    lesson_type = row.get("Тип началка")
                    # Нужны только строки с типом "урок"
                    if lesson_type != "урок":
                        continue
                    start = row.get("Начало началка")
                    end = row.get("Конец началка")
                    lesson_num = row.get("Номер слота")
                else:
                    lesson_type = row.get("Тип старшая")
                    if lesson_type != "урок":
                        continue
                    start = row.get("Начало старшая")
                    end = row.get("Конец старшая")
                    lesson_num = row.get("Номер старшая")

                lesson_data = {
                    "День недели": day_full,
                    "Номер урока": int(lesson_num) if pd.notna(lesson_num) else None,
                    "Начало": start,
                    "Конец": end,
                    "Класс": class_name,
                    "Предмет": subject,
                    "Педагог": (
                        row.get(cfg["teacher_col"])
                        if cfg["teacher_col"] in df.columns
                        and pd.notna(row.get(cfg["teacher_col"]))
                        else ""
                    ),
                    "Тьютор": (
                        row.get(cfg["tutor_col"])
                        if cfg["tutor_col"] in df.columns
                        and pd.notna(row.get(cfg["tutor_col"]))
                        else ""
                    ),
                    "Комната": (
                        row.get(cfg["room_col"])
                        if cfg["room_col"] in df.columns
                        and pd.notna(row.get(cfg["room_col"]))
                        else ""
                    ),
                }

                processed_data.append(lesson_data)

        result_df = pd.DataFrame(processed_data)

        # Упорядочим по дню и номеру урока (для красоты)
        if not result_df.empty:
            day_order = {
                "Понедельник": 1,
                "Вторник": 2,
                "Среда": 3,
                "Четверг": 4,
                "Пятница": 5,
            }
            result_df["__day_order"] = result_df["День недели"].map(day_order)
            result_df = result_df.sort_values(
                ["__day_order", "Номер урока", "Класс"]
            ).drop(columns="__day_order")

        return result_df

    except Exception as e:
        st.error(f"Ошибка при загрузке файла: {e}")
        return pd.DataFrame()


# Загрузка данных
df = load_and_process_data()

print(df.head())

if df.empty:
    st.warning("Не удалось загрузить данные. Проверьте наличие файла 'Расписание 2025.xlsx'")
    st.stop()

# Боковая панель с фильтрами
st.sidebar.header("🔍 Фильтры")

# Фильтр по классу
classes = ["Все"] + sorted(df["Класс"].unique().tolist())
selected_class = st.sidebar.selectbox("Выберите класс:", classes)

# Фильтр по педагогу
teachers = ["Все"] + sorted(df["Педагог"].dropna().unique().tolist())
selected_teacher = st.sidebar.selectbox("Выберите педагога:", teachers)

# Фильтр по предмету
subjects = ["Все"] + sorted(df["Предмет"].dropna().unique().tolist())
selected_subject = st.sidebar.selectbox("Выберите предмет:", subjects)

# Фильтр по кабинету
rooms = ["Все"] + sorted(df["Комната"].dropna().unique().tolist())
selected_room = st.sidebar.selectbox("Выберите кабинет:", rooms)

# Применение фильтров
filtered_df = df.copy()

if selected_class != "Все":
    filtered_df = filtered_df[filtered_df["Класс"] == selected_class]

if selected_teacher != "Все":
    filtered_df = filtered_df[filtered_df["Педагог"] == selected_teacher]

if selected_subject != "Все":
    filtered_df = filtered_df[filtered_df["Предмет"] == selected_subject]

if selected_room != "Все":
    filtered_df = filtered_df[filtered_df["Комната"] == selected_room]

# Основная область отображения
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📅 Расписание уроков")

    if not filtered_df.empty:
        display_df = filtered_df[
            [
                "День недели",
                "Номер урока",
                "Начало",
                "Конец",
                "Класс",
                "Предмет",
                "Педагог",
                "Тьютор",
                "Комната",
            ]
        ].copy()

        # Форматирование времени
        display_df["Начало"] = display_df["Начало"].apply(
            lambda x: x.strftime("%H:%M") if pd.notna(x) else ""
        )
        display_df["Конец"] = display_df["Конец"].apply(
            lambda x: x.strftime("%H:%M") if pd.notna(x) else ""
        )

        st.dataframe(display_df, use_container_width=True, height=400)

        st.metric("Количество уроков", len(filtered_df))
    else:
        st.info("Нет данных, соответствующих выбранным фильтрам")

# Секция для отладки
with st.expander("🔧 Отладочная информация"):
    st.write("**Всего уроков в базе:**", len(df))
    st.write("Доступные классы:", sorted(df["Класс"].unique()))
    st.write("Доступные педагоги:", sorted(df["Педагог"].dropna().unique()))

# Инструкция
st.markdown("---")
st.subheader("ℹ️ Как использовать:")
st.markdown(
    """
1. **Выберите фильтры** в левой панели  
2. **Просматривайте отфильтрованное расписание** в основной области  
3. **Используйте статистику** для быстрого анализа  
4. **Экспортируйте данные** через меню в таблице (если нужно)  
"""
)
