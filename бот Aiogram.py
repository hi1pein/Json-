from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
import asyncio
from map_client import AsyncPl3xMapClient
from config import DEFAULT_BASE_URL

TOKEN = "ВАШ_ТОКЕН"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
map_client = AsyncPl3xMapClient(DEFAULT_BASE_URL)

@dp.message_handler(commands=['players'])
async def cmd_players(message: Message):
    players = map_client.get_players()
    if not players:
        await message.answer("Нет игроков на карте.")
        return
    text = "\n".join(f"{name}: {info}" for name, info in players.items())
    await message.answer(f"```\n{text}\n```", parse_mode='Markdown')

@dp.message_handler(commands=['online'])
async def cmd_online(message: Message):
    await message.answer(f"Онлайн: {len(map_client.get_players())}")

async def on_startup():
    map_client.start()

if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)