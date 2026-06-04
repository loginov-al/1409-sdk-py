import os
import shutil
import json


_SDK_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_DESIGN = os.path.join(_SDK_ROOT, "design")
_DEFAULT_FONTS = os.path.join(_SDK_ROOT, "fonts")


class Client:
    """Клиент дизайн-системы 1409.

    Позволяет получать список доступных UI-компонентов и экспортировать
    их файлы (HTML, CSS и др.) в любую папку проекта.

    Args:
        source: Путь к папке с компонентами. По умолчанию — встроенная
                папка design/ из SDK.
    """

    def __init__(self, source: str = None):
        self._source = source or _DEFAULT_DESIGN

    def list(self) -> list[str]:
        """Возвращает список доступных компонентов."""
        if not os.path.isdir(self._source):
            return []
        return [
            name for name in sorted(os.listdir(self._source))
            if os.path.isdir(os.path.join(self._source, name))
        ]

    def info(self, name: str) -> dict:
        """Возвращает информацию о компоненте."""
        component_dir = os.path.join(self._source, name)
        if not os.path.isdir(component_dir):
            raise ValueError(f"Компонент '{name}' не найден в {self._source}")

        files = [f for f in os.listdir(component_dir) if not f.startswith(".")]

        meta_path = os.path.join(component_dir, "meta.json")
        description = ""
        if os.path.isfile(meta_path):
            with open(meta_path, encoding="utf-8") as f:
                meta = json.load(f)
            description = meta.get("description", "")

        return {
            "name": name,
            "files": sorted(files),
            "description": description,
        }

    def pull(self, name: str, dest: str, format: str = "html") -> str:
        """Копирует файлы компонента в указанную папку."""
        component_dir = os.path.join(self._source, name)
        if not os.path.isdir(component_dir):
            raise ValueError(f"Компонент '{name}' не найден в {self._source}")

        os.makedirs(dest, exist_ok=True)

        if format == "all":
            target = os.path.join(dest, name)
            if os.path.exists(target):
                shutil.rmtree(target)
            shutil.copytree(component_dir, target)
            return target

        if format not in ("html", "css"):
            raise ValueError(f"Неподдерживаемый формат '{format}'. Используйте: html, css, all")

        src_file = os.path.join(component_dir, f"{name}.{format}")
        if not os.path.isfile(src_file):
            raise FileNotFoundError(
                f"Файл '{name}.{format}' не найден в компоненте '{name}'"
            )

        dest_file = os.path.join(dest, f"{name}.{format}")
        shutil.copy2(src_file, dest_file)
        return dest_file

    def pull_all(self, dest: str, format: str = "html") -> list[str]:
        """Копирует все компоненты дизайн-системы в указанную папку."""
        results = []
        for name in self.list():
            try:
                path = self.pull(name, dest=dest, format=format)
                results.append(path)
            except FileNotFoundError:
                pass
        return results

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
