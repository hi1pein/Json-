"""
Пример использования синхронного клиента.
"""

import time
from map_client import Pl3xMapClient
from config import DEFAULT_BASE_URL

def callback(data):
    print("Callback получил данные:", list(data.keys()))

def main():
    client = Pl3xMapClient(DEFAULT_BASE_URL, on_update=callback)
    client.start()

    while True:
        players = client.get_players()
        print(f"Игроков: {len(players)}")
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Выход...")