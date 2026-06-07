# INDX.MONEY Trading Client

Торговый клиент для биржи [INDX.MONEY](https://indx.money/) с графическим интерфейсом на CustomTkinter.

## Возможности

- Просмотр баланса и портфеля
- Создание ордеров на покупку и продажу
- Удаление активных ордеров
- Просмотр списка инструментов биржи
- Просмотр истории торгов
- Просмотр заявок по инструментам
- Статистика сделок (Tick)

## Требования

- Python 3.8+
- Зависимости из `requirements.txt`

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd indxclient
```
2. Установите зависимости:
```bash
pip install -r requirements.txt
```
3. Создайте файл config.json с вашими данными:
```json
{
    "login": "your_login",
    "password": "your_password",
    "wmid": "123456789012",
    "culture": "ru-RU"
}
```
## Запуск GUI

```bash
python3 main.py
```

## Использование API клиента (без GUI)

```python
from api_client import IndoxAPIClient

# Инициализация
api = IndxAPIClient()

# Получить баланс
balance = api.balance()
print(balance)

# Получить список инструментов
tools = api.tools()
print(tools)

# Создать ордер на покупку
response = api.offer_add(
    tool_id=60,      # ID инструмента
    count=0.5,       # Количество (можно дробное)
    is_bid=True,     # True - покупка, False - продажа
    price=80000.0,   # Цена за единицу
    is_anonymous=True # Анонимная заявка
)
print(response)
```
### Коды ошибок API

Код	Описание
0	Запрос выполнен успешно
-1	Сервис остановлен
-2	Доступ запрещен
-3	Ошибочный WMID трейдера
-4	Подпись запроса сформирована не верно
-5	Некорректная дата
-6	Несуществующий номер инструмента
-7	Вызов веб-сервиса завершился ошибкой
-36	Неверное значение поля reqn
-37	Не выполнено условие увеличения reqn
-42	Превышено максимальное количество заявок
