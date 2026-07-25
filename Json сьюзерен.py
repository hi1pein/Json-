"""
Pl3xMap SSE Client
Получение данных с карты Minecraft в реальном времени.
Поддерживает синхронный и асинхронный режимы.
"""

import json
import threading
import time
from typing import Dict, List, Callable, Optional, Any

import requests
from sseclient import SSEClient


class Pl3xMapClient:
    """
    Синхронный клиент для подключения к SSE (Server-Sent Events) карты Pl3xMap.
    """

    def __init__(self, base_url: str, on_update: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.base_url = base_url.rstrip('/')
        self.on_update = on_update
        self._stop = False
        self._thread = None
        self._players: Dict[str, Any] = {}
        self._markers: Dict[str, Any] = {}
        self._last_data: Optional[Dict[str, Any]] = None
        self._event_source = None

    def _get_sse_url(self) -> str:
        """Пытается определить правильный SSE-эндпоинт."""
        candidates = [
            f"{self.base_url}/sse/minecraft-overworld",
            f"{self.base_url}/sse/minecraft:overworld",
            f"{self.base_url}/sse/world",
            f"{self.base_url}/sse/overworld",
            f"{self.base_url}/sse"
        ]
        for url in candidates:
            try:
                resp = requests.get(url, stream=True, timeout=5)
                if resp.status_code == 200:
                    return url
            except Exception:
                continue
        raise RuntimeError("Не удалось найти рабочий SSE-эндпоинт. Проверьте URL карты.")

    def _run(self):
        """Основной цикл чтения SSE-событий."""
        sse_url = self._get_sse_url()
        while not self._stop:
            try:
                response = requests.get(sse_url, stream=True)
                client = SSEClient(response)
                for event in client.events():
                    if self._stop:
                        break
                    if event.data:
                        try:
                            data = json.loads(event.data)
                            self._last_data = data
                            if 'players' in data:
                                self._players = data['players']
                            if 'markers' in data:
                                self._markers = data.get('markers', {})
                            if self.on_update:
                                self.on_update(data)
                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                # В случае ошибки ждём и переподключаемся
                time.sleep(2)

    def start(self):
        """Запускает поток для чтения SSE."""
        if self._thread and self._thread.is_alive():
            return
        self._stop = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """Останавливает поток."""
        self._stop = True
        if self._thread:
            self._thread.join(timeout=3)

    def get_players(self) -> Dict[str, Any]:
        return self._players

    def get_markers(self) -> Dict[str, Any]:
        return self._markers

    def get_last_data(self) -> Optional[Dict[str, Any]]:
        return self._last_data


# ===== Асинхронная версия =====
import asyncio
import aiohttp

class AsyncPl3xMapClient:
    """
    Асинхронный клиент для использования в ботах с asyncio.
    """

    def __init__(self, base_url: str, on_update: Optional[Callable[[Dict[str, Any]], None]] = None):
        self.base_url = base_url.rstrip('/')
        self.on_update = on_update
        self._players: Dict[str, Any] = {}
        self._markers: Dict[str, Any] = {}
        self._last_data: Optional[Dict[str, Any]] = None
        self._running = False
        self._task = None

    async def _get_sse_url(self) -> str:
        candidates = [
            f"{self.base_url}/sse/minecraft-overworld",
            f"{self.base_url}/sse/minecraft:overworld",
            f"{self.base_url}/sse/world",
            f"{self.base_url}/sse/overworld",
            f"{self.base_url}/sse"
        ]
        async with aiohttp.ClientSession() as session:
            for url in candidates:
                try:
                    async with session.get(url, timeout=5) as resp:
                        if resp.status == 200:
                            return url
                except Exception:
                    continue
        raise RuntimeError("Не удалось найти рабочий SSE-эндпоинт.")

    async def _run(self):
        self._running = True
        sse_url = await self._get_sse_url()
        async with aiohttp.ClientSession() as session:
            while self._running:
                try:
                    async with session.get(sse_url) as resp:
                        async for line in resp.content:
                            if not self._running:
                                break
                            if line.startswith(b'data: '):
                                try:
                                    data = json.loads(line[6:].decode('utf-8'))
                                    self._last_data = data
                                    if 'players' in data:
                                        self._players = data['players']
                                    if 'markers' in data:
                                        self._markers = data.get('markers', {})
                                    if self.on_update:
                                        self.on_update(data)
                                except Exception:
                                    continue
                except Exception:
                    await asyncio.sleep(2)

    def start(self):
        if self._task and not self._task.done():
            return
        self._running = True
        self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    def get_players(self) -> Dict[str, Any]:
        return self._players

    def get_markers(self) -> Dict[str, Any]:
        return self._markers

    def get_last_data(self) -> Optional[Dict[str, Any]]:
        return self._last_data


# ===== Пример использования =====
if __name__ == "__main__":
    # Синхронный вариант
    def on_update(data):
        print(f"[UPDATE] Получены данные: {data.keys()}")
        if 'players' in data:
            for name, info in data['players'].items():
                print(f"  {name}: {info}")

    client = Pl3xMapClient("https://map.suzeren.org", on_update=on_update)
    client.start()

    try:
        while True:
            players = client.get_players()
            print(f"[INFO] Игроков онлайн: {len(players)}")
            time.sleep(5)
    except KeyboardInterrupt:
        client.stop()
        print("Клиент остановлен.")

    # Асинхронный пример (для ботов)
    # async def main():
    #     async def async_callback(data):
    #         print(f"Async update: {data}")
    #
    #     async_client = AsyncPl3xMapClient("https://map.suzeren.org", on_update=async_callback)
    #     async_client.start()
    #     await asyncio.sleep(30)
    #     await async_client.stop()
    #
    # asyncio.run(main())