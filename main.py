from datetime import date
import calendar

doc_number = "WRT-2026-001"
client_name = "Иванов Иван Иванович"
product_name = "Ноутбук Lenovo IdeaPad 3"
seller = "ООО «ТехноМир»"
start_date = date(2026, 9, 1)

warranty_months = 31


# 1. дата окончания гарантии
def calculate_end_date(start_date, months):
    total_months = start_date.month + months - 1
    year = start_date.year + total_months // 12
    month = total_months % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    day = min(start_date.day, last_day)
    return date(year, month, day)


# 2. статус гарантии
def get_warranty_status(end_date):
    today = date.today()
    if today > end_date:
        return "Гарантия истекла"
    elif today == end_date:
        return "Последний день гарантии"
    else:
        return "Гарантия действует"


# 3. дней до окончания
def days_until_expiration(end_date):
    today = date.today()
    delta = (end_date - today).days
    if delta < 0:
        return 0
    return delta


# 4. уведомление
def get_expiration_notice(days_left):
    if days_left == 0:
        return "Уведомление: гарантия уже истекла"
    elif days_left <= 30:
        return "Уведомление: гарантия истекает в течение месяца!"
    else:
        return "Гарантия в порядке, уведомлений нет"


end_date = calculate_end_date(start_date, warranty_months)
status = get_warranty_status(end_date)
days_left = days_until_expiration(end_date)
notice = get_expiration_notice(days_left)

print("===== Гарантийный документ =====")
print(f"Номер документа : {doc_number}")
print(f"Клиент          : {client_name}")
print(f"Товар           : {product_name}")
print(f"Продавец        : {seller}")
print(f"Дата начала     : {start_date}")
print(f"Срок гарантии   : {warranty_months} мес.")
print(f"Дата окончания  : {end_date}")
print("--------------------------------")
print(f"Статус          : {status}")
print(f"Осталось дней   : {days_left}")
print(notice)