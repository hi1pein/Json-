"""
Конфигурация клиента.
Можно переопределять через переменные окружения.
"""

import os

DEFAULT_BASE_URL = os.getenv("PL3XMAP_URL", "https://map.suzeren.org")
DEFAULT_RECONNECT_DELAY = int(os.getenv("PL3XMAP_RECONNECT_DELAY", "2"))
DEFAULT_LOG_LEVEL = os.getenv("PL3XMAP_LOG_LEVEL", "INFO")