from __future__ import annotations

from importlib import import_module
from pkgutil import iter_modules


def import_all_models() -> None:
    """Import every model module so Alembic autogenerate can see table metadata."""
    package_name = __name__
    package_path = __path__

    for module_info in iter_modules(package_path):
        if module_info.name.startswith("_"):
            continue
        import_module(f"{package_name}.{module_info.name}")
