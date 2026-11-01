import pdfplumber
import re
import json
from datetime import date, timedelta, datetime
from zoneinfo import ZoneInfo

PDF_FILE = "schedule.pdf"

SUBGROUP = "01"

# Начало первого известного двухнедельного периода
BASE_START_DATE = date(2026, 10, 26)

# Текущая дата по московскому времени
today = datetime.now(ZoneInfo("Europe/Moscow")).date()

# Определяем номер двухнедельного периода
days_from_base = (today - BASE_START_DATE).days
period_number = days_from_base // 14

# Начало текущего двухнедельного периода
START_DATE = BASE_START_DATE + timedelta(days=period_number * 14)


def clean_text(text):
    if not text:
        return ""

    return re.sub(r"\s+", " ", text).strip()


def split_lessons(text):
    """
    Разделяет содержимое ячейки на отдельные занятия.
    """

    text = clean_text(text)

    parts = re.split(
        r"(?=ФИб-2301-51-00,\s*\d{2}\s*подгруппа)",
        text
    )

    return [part.strip() for part in parts if part.strip()]


def get_subgroup(text):
    match = re.search(
        r"ФИб-2301-51-00,\s*(\d{2})\s*подгруппа",
        text
    )

    if match:
        return match.group(1)

    return None


def parse_lesson(text):
    text = clean_text(text)

    subgroup = get_subgroup(text)

    # Убираем информацию о группе
    text = re.sub(
        r"ФИб-2301-51-00,\s*\d{2}\s*подгруппа\s*",
        "",
        text
    )

    # Аудитория
    room_match = re.search(r"(\d+-\d+)$", text)

    room = ""

    if room_match:
        room = room_match.group(1)
        text = text[:room_match.start()].strip()

    # Преподаватель
    teacher_match = re.search(
        r"([А-ЯЁ][а-яё-]+\s+[А-ЯЁ]\.\s*[А-ЯЁ]\.)$",
        text
    )

    teacher = ""

    if teacher_match:
        teacher = teacher_match.group(1)
        text = text[:teacher_match.start()].strip()

    # Тип занятия
    type_match = re.search(
        r"\b(Лекция|Лабораторная работа|Практическое занятие)\b",
        text
    )

    lesson_type = ""

    if type_match:
        lesson_type = type_match.group(1)
        subject = text[:type_match.start()].strip()
    else:
        subject = text

    return {
        "subgroup": subgroup,
        "subject": subject,
        "type": lesson_type,
        "teacher": teacher,
        "room": room
    }


def parse_pdf():
    schedule = {}

    current_date = None
    current_time = None
    day_number = -1

    with pdfplumber.open(PDF_FILE) as pdf:

        for page in pdf.pages:

            tables = page.extract_tables()

            for table in tables:

                for row in table:

                    if not row or len(row) < 3:
                        continue

                    # Пропускаем заголовок
                    if row[0] == "День":
                        continue

                    # Новый день
                    if row[0] is not None:
                        day_number += 1
                        current_date = START_DATE + timedelta(
                            days=day_number
                        )

                    # Новый интервал
                    if row[1] is not None:
                        current_time = clean_text(row[1])

                    text = clean_text(row[2])

                    if not text:
                        continue

                    lessons = split_lessons(text)

                    for lesson_text in lessons:

                        subgroup = get_subgroup(lesson_text)

                        # Если занятие относится к другой подгруппе
                        if subgroup is not None and subgroup != SUBGROUP:
                            continue

                        lesson = parse_lesson(lesson_text)

                        if "Элективные дисциплины (модули) по физической культуре и спорту" in lesson["subject"]:
                            if lesson["teacher"] != "Полубоярцев С.А.":
                                continue

                        date_str = current_date.strftime("%d.%m.%Y")

                        if date_str not in schedule:
                            schedule[date_str] = {}

                        if current_time not in schedule[date_str]:
                            schedule[date_str][current_time] = []

                        schedule[date_str][current_time].append(
                            lesson
                        )

    return schedule


schedule = parse_pdf()


with open("schedule.json", "w", encoding="utf-8") as file:
    json.dump(schedule, file, ensure_ascii=False, indent=4)

print("Расписание сохранено в schedule.json")
