import requests
from datetime import date, timedelta

GROUP = "26570_1"

# Начало первого известного двухнедельного периода
BASE_START_DATE = date(2026, 10, 26)

today = date.today()

# Определяем номер двухнедельного периода
days_from_base = (today - BASE_START_DATE).days
period_number = days_from_base // 14

# Начало текущего двухнедельного периода
start = BASE_START_DATE + timedelta(days=period_number * 14)

# Конец двухнедельного периода
end = start + timedelta(days=13)

start_str = start.strftime("%d%m%Y")
end_str = end.strftime("%d%m%Y")

url = (
    f"https://old.vyatsu.ru/reports/schedule/Group/"
    f"{GROUP}_{start_str}_{end_str}.pdf"
)

print("Ссылка:")
print(url)

response = requests.get(url, timeout=30)
response.raise_for_status()

if not response.content.startswith(b"%PDF"):
    raise Exception("Сервер вернул файл, который не является PDF")

with open("schedule.pdf", "wb") as file:
    file.write(response.content)

print("Расписание скачано!")
