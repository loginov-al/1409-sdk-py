import os
import shutil
from .request_modal.api import get, get_text, get_list, link_tag

_SDK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_FONTS = os.path.join(_SDK_ROOT, "fonts")


class Client:
    """Клиент дизайн-системы 1409.

    Все запросы выполняются через request_modal/api.py.
    """

    def get(self, component: str) -> bytes:
        """Возвращает компонент в байтах."""
        return get(component)

    def get_text(self, component: str) -> str:
        """Возвращает компонент как строку (HTML, CSS и др.)."""
        return get_text(component)

    def link_tag(self, component: str) -> str:
        """Возвращает готовый HTML-тег для подключения компонента.

        Example:
            client.link_tag("logo")
            # '<img src="https://api.my1409.ru/design?component=logo" alt="logo">'

            client.link_tag("button")
            # '<link rel="stylesheet" href="https://api.my1409.ru/design?component=button">'
        """
        return link_tag(component)

    def pull(self, component: str, dest: str) -> str:
        """Скачивает компонент и сохраняет файл в указанную папку."""
        data = get(component)
        os.makedirs(dest, exist_ok=True)
        dest_file = os.path.join(dest, component)
        with open(dest_file, "wb") as f:
            f.write(data)
        return dest_file

    def list(self) -> list[str]:
        """Возвращает список доступных компонентов с сервера."""
        return get_list()

    def fonts(self, dest: str) -> list[str]:
        """Копирует шрифты дизайн-системы в указанную папку."""
        os.makedirs(dest, exist_ok=True)
        copied = []
        if not os.path.isdir(_DEFAULT_FONTS):
            return copied
        for font_file in sorted(os.listdir(_DEFAULT_FONTS)):
            if font_file.endswith(".ttf") or font_file.endswith(".otf"):
                src = os.path.join(_DEFAULT_FONTS, font_file)
                dst = os.path.join(dest, font_file)
                shutil.copy2(src, dst)
                copied.append(dst)
        return copied
