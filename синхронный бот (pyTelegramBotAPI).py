import telebot
import threading
from map_client import Pl3xMapClient
from config import DEFAULT_BASE_URL

TOKEN = "ВАШ_ТОКЕН"

bot = telebot.TeleBot(TOKEN)
client = Pl3xMapClient(DEFAULT_BASE_URL)

def start_map():
    client.start()

threading.Thread(target=start_map, daemon=True).start()

@bot.message_handler(commands=['players'])
def send_players(message):
    players = client.get_players()
    bot.reply_to(message, str(players))

@bot.message_handler(commands=['online'])
def send_online(message):
    bot.reply_to(message, f"Онлайн: {len(client.get_players())}")

bot.polling()