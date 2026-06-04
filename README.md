# 1409 SDK

Python SDK для работы с дизайн-системой 1409.  
Подключай UI-компоненты (лого, фон, кнопки и др.) в любой Python-проект через один импорт.

## Установка

```bash
pip install 1409sdk
```

## Быстрый старт

```python
from sdk1409.client import Client

client = Client()

# Получить HTML-тег компонента
print(client.link_tag("logo"))
# <img src="https://api.my1409.ru/design?component=logo" alt="logo">

print(client.link_tag("button"))
# <link rel="stylesheet" href="https://api.my1409.ru/design?component=button">

# Вставить в HTML-шаблон
logo_tag = client.link_tag("logo")
html = f"<html><body>{logo_tag}</body></html>"

# Скачать компонент в проект
client.pull("logo", dest="./assets/")

# Скопировать шрифты
client.fonts(dest="./assets/fonts/")
```

## Методы

| Метод | Описание |
|-------|----------|
| `link_tag(component)` | Готовый HTML-тег для вставки на страницу |
| `get(component)` | Содержимое компонента в байтах |
| `get_text(component)` | Содержимое компонента как строка |
| `pull(component, dest)` | Скачать и сохранить файл |
| `list()` | Список доступных компонентов |
| `fonts(dest)` | Копировать шрифты в проект |

## Документация

Подробная документация в [docs/Doc.md](docs/Doc.md).

## Лицензия

MIT
