import requests
from datetime import date, timedelta


GROUP = "26570_1"


today = date.today()

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

response = requests.get(url)

if response.status_code == 200:
    with open("schedule.pdf", "wb") as file:
        file.write(response.content)

    print("Расписание скачано!")
else:
    print("Ошибка:", response.status_code)
