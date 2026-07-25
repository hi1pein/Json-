"""
Тестирование подключения к карте.
"""

import time
from map_client import Pl3xMapClient
from config import DEFAULT_BASE_URL

def on_update(data):
    print(f"[TEST] Получено обновление: {list(data.keys())}")

def main():
    print(f"Подключение к {DEFAULT_BASE_URL}...")
    client = Pl3xMapClient(DEFAULT_BASE_URL, on_update=on_update)
    client.start()

    try:
        for i in range(10):
            players = client.get_players()
            print(f"[TEST] Игроков онлайн: {len(players)}")
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        client.stop()
        print("[TEST] Клиент остановлен.")

if __name__ == "__main__":
    main()