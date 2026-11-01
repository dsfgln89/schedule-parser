import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


GROUP = "26570_1"

# Получаем текущую дату по московскому времени
today = datetime.now(ZoneInfo("Europe/Moscow")).date()

# Понедельник текущей недели
start = today - timedelta(days=today.weekday())

# Воскресенье следующей недели
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

# Проверяем, что действительно скачали PDF
if not response.content.startswith(b"%PDF"):
    raise Exception("Сервер вернул файл, который не является PDF")

with open("schedule.pdf", "wb") as file:
    file.write(response.content)

# Сохраняем дату начала расписания для парсера
with open("schedule_start_date.txt", "w", encoding="utf-8") as file:
    file.write(start.isoformat())

print("Расписание скачано!")
