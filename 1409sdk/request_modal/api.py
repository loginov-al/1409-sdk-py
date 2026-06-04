import urllib.request
import urllib.error
import json

BASE_URL = "https://api.my1409.ru"

# Типы компонентов → HTML-тег
_TAG_MAP = {
    "logo":       "img",
    "background": "img",
    "icon":       "link-icon",
    "font":       "link-font",
}


def _build_url(component: str) -> str:
    return f"{BASE_URL}/design?component={component}"


def get(component: str) -> bytes:
    """Запрашивает компонент с сервера.

    Args:
        component: Название компонента — 'logo', 'background', 'button' и т.д.

    Returns:
        Содержимое компонента в байтах.

    Raises:
        ValueError:      При ответе сервера с ошибкой (4xx, 5xx).
        ConnectionError: При проблемах с сетью.
    """
    url = _build_url(component)
    try:
        with urllib.request.urlopen(url) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        raise ValueError(f"Ошибка сервера {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise ConnectionError(f"Не удалось подключиться к {BASE_URL}: {e.reason}")


def get_text(component: str) -> str:
    """Запрашивает компонент и возвращает его как строку (HTML, CSS и др.)."""
    return get(component).decode("utf-8")


def get_list() -> list[str]:
    """Возвращает список доступных компонентов с сервера."""
    url = f"{BASE_URL}/design/list"
    try:
        with urllib.request.urlopen(url) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ValueError(f"Ошибка сервера {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise ConnectionError(f"Не удалось подключиться к {BASE_URL}: {e.reason}")


def link_tag(component: str) -> str:
    """Возвращает готовый HTML-тег для подключения компонента на странице.

    Тип тега определяется по названию компонента:
    - logo, background → <img src="...">
    - icon             → <link rel="icon" href="...">
    - font             → <link rel="preload" href="..." as="font">
    - всё остальное    → <link rel="stylesheet" href="...">

    Args:
        component: Название компонента.

    Returns:
        Строка с HTML-тегом.

    Example:
        >>> link_tag("logo")
        '<img src="https://api.my1409.ru/design?component=logo" alt="logo">'

        >>> link_tag("icon")
        '<link rel="icon" href="https://api.my1409.ru/design?component=icon">'

        >>> link_tag("button")
        '<link rel="stylesheet" href="https://api.my1409.ru/design?component=button">'
    """
    url = _build_url(component)
    tag_type = _TAG_MAP.get(component, "link-stylesheet")

    if tag_type == "img":
        return f'<img src="{url}" alt="{component}">'
    elif tag_type == "link-icon":
        return f'<link rel="icon" href="{url}">'
    elif tag_type == "link-font":
        return f'<link rel="preload" href="{url}" as="font" crossorigin="anonymous">'
    else:
        return f'<link rel="stylesheet" href="{url}">'
