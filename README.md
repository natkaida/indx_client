# INDX.MONEY Trading Client

Торговый клиент для биржи [INDX.MONEY](https://indx.money/) с графическим интерфейсом на CustomTkinter.

<img width="1246" height="859" alt="screen1" src="https://github.com/user-attachments/assets/0a4122d5-0651-45d7-8063-61e4112024f5" />

## Возможности

- Просмотр баланса и портфеля
- Создание ордеров на покупку и продажу
- Удаление активных ордеров
- Просмотр списка инструментов биржи
- Просмотр истории торгов
- Просмотр заявок по инструментам
- Статистика сделок (Tick)

<img width="1231" height="857" alt="screen2" src="https://github.com/user-attachments/assets/e9d13595-be03-4ccf-97a9-7a48e8443c03" />

## Требования

- Python 3.8+
- Зависимости из `requirements.txt`

<img width="1226" height="857" alt="screen3" src="https://github.com/user-attachments/assets/b7430d62-468e-4244-9780-dd8603a2c34c" />

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

<img width="1224" height="849" alt="screen4" src="https://github.com/user-attachments/assets/e84d164d-d87a-455a-8abd-4c195057ec80" />

## Запуск GUI

```bash
python3 main.py
```
<img width="1232" height="853" alt="screen5" src="https://github.com/user-attachments/assets/5d22fee2-ac35-41dd-877a-ec9279d06e56" />

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
<img width="1231" height="852" alt="screen6" src="https://github.com/user-attachments/assets/2d3c1b6e-0e64-46da-a6e4-ff08770fbce2" />

### Коды ошибок API

- 0	    Запрос выполнен успешно
- -1    Сервис остановлен
- -2	Доступ запрещен
- -3	Ошибочный WMID трейдера
- -4	Подпись запроса сформирована не верно
- -5	Некорректная дата
- -6	Несуществующий номер инструмента
- -7	Вызов веб-сервиса завершился ошибкой
- -36	Неверное значение поля reqn
- -37	Не выполнено условие увеличения reqn
- -42	Превышено максимальное количество заявок

<img width="1234" height="852" alt="screen7" src="https://github.com/user-attachments/assets/142762c2-9729-4594-9559-052cfa942ad4" />
