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
    # Пытаемся найти файл в разных местах
    possible_paths = [
        'Schedule_to_prog.xlsx',
        './Schedule_to_prog.xlsx',
        'data/Schedule_to_prog.xlsx'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return pd.read_excel(path, sheet_name='Sheet1', header=0)
    
    st.error("Файл с расписанием не найден")
    return None

@st.cache_data
def load_and_process_data():
    try:
        df = load_data()
        if df is None:
            return pd.DataFrame()
        
        # Создаем список для хранения преобразованных данных
        processed_data = []
        
        # Проходим по каждой строке исходных данных
        for idx, row in df.iterrows():
            if pd.isna(row['День недели']):
                continue
                
            # Базовая информация об уроке
            base_info = {
                'День недели': row['День недели'],
                'Номер урока': row['Номер урока'],
                'Начало': row['Начало'],
                'Конец': row['Конец']
            }
            
            # Обрабатываем все классы включая Старт
            classes_info = {
                'Старт': {'subject_col': 'Старт', 'teacher_col': 'Педагог', 'tutor_col': 'Тьютор', 'room_col': 'Комната'},
                '1 класс': {'subject_col': '1 класс', 'teacher_col': 'Педагог.1', 'tutor_col': 'Тьютор.1', 'room_col': 'Комната.1'},
                '2 класс': {'subject_col': '2 класс', 'teacher_col': 'Педагог.2', 'tutor_col': 'Тьютор.2', 'room_col': 'Комната.2'},
                '3 класс': {'subject_col': '3 класс', 'teacher_col': 'Педагог.3', 'tutor_col': 'Тьютор.3', 'room_col': 'Комната.3'},
                '4 класс': {'subject_col': '4 класс', 'teacher_col': 'Педагог.4', 'tutor_col': 'Тьютор.4', 'room_col': 'Комната.4'},
                '5 класс': {'subject_col': '5 класс', 'teacher_col': 'Педагог.5', 'tutor_col': 'Тьютор.5', 'room_col': 'Комната.5'},
                '6 класс': {'subject_col': '6 класс', 'teacher_col': 'Педагог.6', 'tutor_col': 'Тьютор.6', 'room_col': 'Комната.6'},
                '7 класс': {'subject_col': '7 класс', 'teacher_col': 'Педагог.7', 'tutor_col': 'Тьютор.7', 'room_col': 'Комната.7'},
                '8 класс': {'subject_col': '8 класс', 'teacher_col': 'Педагог.8', 'tutor_col': 'Тьютор.8', 'room_col': 'Комната.8'},
                '9 класс': {'subject_col': '9 класс', 'teacher_col': 'Педагог.9', 'tutor_col': 'Тьютор.9', 'room_col': 'Комната.9'},
            }
            
            for class_name, cols in classes_info.items():
                subject = row[cols['subject_col']]
                if pd.isna(subject) or subject == '':
                    continue
                    
                lesson_data = base_info.copy()
                lesson_data.update({
                    'Класс': class_name,
                    'Предмет': subject,
                    'Педагог': row[cols['teacher_col']] if not pd.isna(row[cols['teacher_col']]) else '',
                    'Тьютор': row[cols['tutor_col']] if not pd.isna(row[cols['tutor_col']]) else '',
                    'Комната': row[cols['room_col']] if not pd.isna(row[cols['room_col']]) else ''
                })
                processed_data.append(lesson_data)
        
        return pd.DataFrame(processed_data)
    
    except Exception as e:
        st.error(f"Ошибка при загрузке файла: {e}")
        return pd.DataFrame()

# Загрузка данных
df = load_and_process_data()

if df.empty:
    st.warning("Не удалось загрузить данные. Проверьте наличие файла 'Schedule_to_prog.xlsx'")
    st.stop()

# Боковая панель с фильтрами
st.sidebar.header("🔍 Фильтры")

# Фильтр по классу
classes = ['Все'] + sorted(df['Класс'].unique().tolist())
selected_class = st.sidebar.selectbox("Выберите класс:", classes)

# Фильтр по педагогу
teachers = ['Все'] + sorted(df['Педагог'].dropna().unique().tolist())
selected_teacher = st.sidebar.selectbox("Выберите педагога:", teachers)

# Фильтр по предмету
subjects = ['Все'] + sorted(df['Предмет'].dropna().unique().tolist())
selected_subject = st.sidebar.selectbox("Выберите предмет:", subjects)

# Фильтр по кабинету
rooms = ['Все'] + sorted(df['Комната'].dropna().unique().tolist())
selected_room = st.sidebar.selectbox("Выберите кабинет:", rooms)

# Применение фильтров
filtered_df = df.copy()

if selected_class != 'Все':
    filtered_df = filtered_df[filtered_df['Класс'] == selected_class]

if selected_teacher != 'Все':
    filtered_df = filtered_df[filtered_df['Педагог'] == selected_teacher]

if selected_subject != 'Все':
    filtered_df = filtered_df[filtered_df['Предмет'] == selected_subject]

if selected_room != 'Все':
    filtered_df = filtered_df[filtered_df['Комната'] == selected_room]

# Основная область отображения
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("📅 Расписание уроков")
    
    if not filtered_df.empty:
        # Красивое отображение таблицы
        display_df = filtered_df[['День недели', 'Номер урока', 'Начало', 'Конец', 'Класс', 
                                'Предмет', 'Педагог', 'Тьютор', 'Комната']].copy()
        
        # Форматирование времени
        display_df['Начало'] = display_df['Начало'].apply(lambda x: x.strftime('%H:%M') if not pd.isna(x) else '')
        display_df['Конец'] = display_df['Конец'].apply(lambda x: x.strftime('%H:%M') if not pd.isna(x) else '')
        
        st.dataframe(display_df, use_container_width=True, height=400)
        
        # Статистика
        st.metric("Количество уроков", len(filtered_df))
    else:
        st.info("Нет данных, соответствующих выбранным фильтрам")


# Секция для отладки (можно скрыть)
with st.expander("🔧 Отладочная информация"):
    st.write("**Исходная структура данных:**")
    st.write(f"Всего уроков в базе: {len(df)}")
    st.write("Доступные классы:", sorted(df['Класс'].unique()))
    st.write("Доступные педагоги:", sorted(df['Педагог'].dropna().unique()))

# Инструкция
st.markdown("---")
st.subheader("ℹ️ Как использовать:")
st.markdown("""
1. **Выберите фильтры** в левой панели
2. **Просматривайте отфильтрованное расписание** в основной области
3. **Используйте статистику** для быстрого анализа
4. **Экспортируйте данные** через меню в таблице (если нужно)
""")