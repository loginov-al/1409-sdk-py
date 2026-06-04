# 1409 SDK — Документация

SDK для использования дизайн-системы 1409 в Python-проектах.
Позволяет подключать готовые UI-компоненты и экспортировать их в HTML и другие форматы.

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
│   └── client.py       # Клиент для работы с компонентами
├── design/             # Референсы UI-компонентов дизайн-системы 1409
│   ├── button/
│   ├── card/
│   └── ...
├── fonts/              # Шрифты дизайн-системы
│   ├── Montserrat-Bold.ttf
│   ├── Montserrat-Regular.ttf
│   └── Roboto-Regular.ttf
└── docs/
    └── Doc.md
```

---

## Быстрый старт

```python
from 1409sdk.client import Client

client = Client()

# Посмотреть доступные компоненты
components = client.list()
print(components)
# ['button', 'card', 'input', 'navbar', ...]

# Экспортировать компонент в папку проекта
client.pull("button", dest="./my-project/components/")

# Экспортировать сразу несколько компонентов
client.pull_all(dest="./my-project/components/")
```

---

## Client

### `Client(source=None)`

Создаёт клиент для работы с дизайн-системой.

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `source` | `str` | Встроенная папка `design/` | Путь к папке с компонентами |

```python
# Использовать встроенные компоненты SDK
client = Client()

# Использовать собственную папку с компонентами
client = Client(source="/path/to/custom/design/")
```

---

### `client.list() → list[str]`

Возвращает список доступных компонентов.

```python
client = Client()
components = client.list()
# ['button', 'card', 'input', 'modal', 'navbar']
```

---

### `client.info(name) → dict`

Возвращает информацию о компоненте.

| Параметр | Тип | Описание |
|----------|-----|----------|
| `name` | `str` | Название компонента |

```python
info = client.info("button")
# {
#   "name": "button",
#   "files": ["button.html", "button.css"],
#   "description": "Кнопка дизайн-системы 1409"
# }
```

---

### `client.pull(name, dest, format="html") → str`

Копирует файлы компонента в указанную папку проекта.

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `name` | `str` | — | Название компонента |
| `dest` | `str` | — | Путь назначения |
| `format` | `str` | `"html"` | Формат экспорта: `"html"`, `"css"`, `"all"` |

```python
# Скопировать HTML компонента
client.pull("button", dest="./src/components/")

# Скопировать только CSS
client.pull("button", dest="./src/styles/", format="css")

# Скопировать все файлы компонента
client.pull("button", dest="./src/components/", format="all")
```

Возвращает путь к скопированному файлу.

---

### `client.pull_all(dest, format="html") → list[str]`

Копирует все компоненты дизайн-системы в указанную папку.

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `dest` | `str` | — | Путь назначения |
| `format` | `str` | `"html"` | Формат экспорта |

```python
# Экспортировать все компоненты в проект
paths = client.pull_all(dest="./src/components/")
print(paths)
# ['./src/components/button.html', './src/components/card.html', ...]
```

---

### `client.fonts(dest) → list[str]`

Копирует шрифты дизайн-системы в указанную папку.

```python
client.fonts(dest="./src/fonts/")
# ['./src/fonts/Montserrat-Bold.ttf', './src/fonts/Roboto-Regular.ttf', ...]
```

---

## Сценарии использования

### Инициализация нового проекта

```python
from 1409sdk.client import Client

client = Client()

# Скопировать все компоненты и шрифты в проект
client.pull_all(dest="./my-app/components/")
client.fonts(dest="./my-app/fonts/")
```

### Использование отдельного компонента

```python
from 1409sdk.client import Client

client = Client()
client.pull("card", dest="./templates/")
```

### Интеграция в Flask / Jinja2

```python
from flask import Flask, render_template_string
from 1409sdk.client import Client
import os

app = Flask(__name__)
client = Client()

# Экспортируем компоненты при запуске
client.pull_all(dest="./templates/components/")

@app.route("/")
def index():
    with open("./templates/components/card.html") as f:
        card = f.read()
    return render_template_string(card)
```

---

## Шрифты дизайн-системы

SDK включает готовые шрифты:

| Файл | Применение |
|------|-----------|
| `Montserrat-Bold.ttf` | Заголовки |
| `Montserrat-Regular.ttf` | Подзаголовки |
| `Roboto-Regular.ttf` | Основной текст |
| `DejaVuSans.ttf` | Запасной шрифт (поддержка Unicode) |

---

## Добавление собственных компонентов в `design/`

Каждый компонент — папка с файлами:

```
design/
└── my-component/
    ├── my-component.html   # Разметка компонента
    ├── my-component.css    # Стили
    └── meta.json           # Описание (опционально)
```

Пример `meta.json`:

```json
{
  "name": "my-component",
  "description": "Мой компонент",
  "version": "1.0.0"
}
```

После этого компонент станет доступен через `client.list()` и `client.pull()`.

---

## Лицензия

MIT