# 1409 SDK — Документация

Python SDK для работы с дизайн-системой 1409.  
Позволяет запрашивать UI-компоненты (лого, фон, кнопки и др.) с сервера `api.my1409.ru` и использовать их в любом Python-проекте.

---

## Установка

```bash
pip install 1409sdk
```

Или локально из репозитория:

```bash
git clone https://github.com/loginov-al/1409-sdk-py.git
cd 1409-sdk-py
pip install -e .
```

---

## Структура SDK

```
1409-sdk-py/
├── 1409sdk/
│   ├── client.py               # Основной клиент
│   └── request_modal/
│       └── api.py              # HTTP-запросы к api.my1409.ru
├── fonts/                      # Шрифты дизайн-системы
│   ├── Montserrat-Bold.ttf
│   ├── Montserrat-Regular.ttf
│   └── Roboto-Regular.ttf
└── docs/
    └── Doc.md
```

---

## Как это работает

```
Ваш код (Python / HTML)
        ↓
  Client.get("logo")
        ↓
  GET https://api.my1409.ru/design?component=logo
        ↓
  Сервер возвращает компонент (изображение, HTML и др.)
```

---

## Быстрый старт

```python
from 1409sdk.client import Client

client = Client()

# Получить лого
logo = client.get("logo")          # bytes

# Получить фон как строку HTML/CSS
background = client.get_text("background")

# Скачать компонент в папку проекта
client.pull("logo", dest="./assets/")
# сохранит файл ./assets/logo
```

---

## Client

### `Client()`

Создаёт клиент для работы с `api.my1409.ru`. Авторизация не требуется.

```python
from 1409sdk.client import Client

client = Client()
```

---

### `client.get(component) → bytes`

Запрашивает компонент с сервера и возвращает его в байтах.

| Параметр    | Тип   | Описание                                   |
|-------------|-------|--------------------------------------------|
| `component` | `str` | Название компонента: `'logo'`, `'background'`, `'button'` и т.д. |

```python
logo_bytes = client.get("logo")
background_bytes = client.get("background")
```

---

### `client.get_text(component) → str`

Запрашивает компонент и возвращает его как строку (для HTML, CSS и подобных форматов).

```python
html = client.get_text("navbar")
css = client.get_text("button")
```

---

### `client.pull(component, dest) → str`

Скачивает компонент и сохраняет файл в указанную папку.

| Параметр    | Тип   | Описание             |
|-------------|-------|----------------------|
| `component` | `str` | Название компонента  |
| `dest`      | `str` | Папка назначения     |

```python
client.pull("logo", dest="./assets/")
# → ./assets/logo

client.pull("background", dest="./static/img/")
# → ./static/img/background
```

---

### `client.list() → list[str]`

Возвращает список всех доступных компонентов с сервера.

```python
components = client.list()
# ['logo', 'background', 'button', 'card', ...]
```

---

### `client.fonts(dest) → list[str]`

Копирует шрифты дизайн-системы в указанную папку.

```python
client.fonts(dest="./static/fonts/")
# ['./static/fonts/Montserrat-Bold.ttf', ...]
```

---

## Сценарии использования

### Скачать все нужные компоненты в проект

```python
from 1409sdk.client import Client

client = Client()

client.pull("logo", dest="./assets/")
client.pull("background", dest="./assets/")
client.fonts(dest="./assets/fonts/")
```

### Использовать компонент напрямую в коде

```python
from 1409sdk.client import Client

client = Client()

# Получить HTML кнопки и вставить в шаблон
button_html = client.get_text("button")

page = f"""
<html>
  <body>
    {button_html}
  </body>
</html>
"""
```

### Интеграция в Flask

```python
from flask import Flask, render_template_string
from 1409sdk.client import Client

app = Flask(__name__)
client = Client()

@app.route("/")
def index():
    logo = client.get_text("logo")
    return render_template_string(f"<html><body>{logo}</body></html>")
```

---

## Шрифты дизайн-системы

| Файл                    | Применение         |
|-------------------------|--------------------|
| `Montserrat-Bold.ttf`   | Заголовки          |
| `Montserrat-Regular.ttf`| Подзаголовки       |
| `Roboto-Regular.ttf`    | Основной текст     |
| `DejaVuSans.ttf`        | Запасной (Unicode) |

---

## API

SDK обращается к `https://api.my1409.ru`.

| Метод | Путь              | Параметр            | Описание                         |
|-------|-------------------|---------------------|----------------------------------|
| GET   | `/design`         | `component=<name>`  | Возвращает компонент             |
| GET   | `/design/list`    | —                   | Список доступных компонентов     |

---

## Лицензия

MIT
