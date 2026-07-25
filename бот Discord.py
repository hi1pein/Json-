import discord
from discord.ext import commands
from map_client import AsyncPl3xMapClient
from config import DEFAULT_BASE_URL

TOKEN = "ВАШ_ТОКЕН"

bot = commands.Bot(command_prefix='!')
map_client = AsyncPl3xMapClient(DEFAULT_BASE_URL)

@bot.event
async def on_ready():
    map_client.start()
    print(f"Бот {bot.user} запущен, карта подключена")

@bot.command()
async def players(ctx):
    players = map_client.get_players()
    if not players:
        await ctx.send("Игроки не найдены.")
        return
    msg = "\n".join(f"{name}: {info}" for name, info in players.items())
    await ctx.send(f"```\n{msg}\n```")

@bot.command()
async def online(ctx):
    await ctx.send(f"Онлайн: {len(map_client.get_players())}")

if __name__ == "__main__":
    bot.run(TOKEN)