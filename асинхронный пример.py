"""
Пример использования асинхронного клиента.
"""

import asyncio
from map_client import AsyncPl3xMapClient
from config import DEFAULT_BASE_URL

async def callback(data):
    print("Async callback:", list(data.keys()))

async def main():
    client = AsyncPl3xMapClient(DEFAULT_BASE_URL, on_update=callback)
    client.start()
    await asyncio.sleep(30)
    await client.stop()

if __name__ == "__main__":
    asyncio.run(main())