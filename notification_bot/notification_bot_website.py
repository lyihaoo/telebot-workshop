import os
from time import sleep
from dotenv import load_dotenv
import requests

from telegram import Bot

load_dotenv("../.env")
TOKEN = os.getenv("token")
CHAT_ID = os.getenv("chat_id")

bot = Bot(TOKEN)

while(True):
    try:
        response = requests.head("http://www.google.com")
        if response.status_code == 200:
            message = "Website is alive"
        else:
            message = "Website is down"
    except:
        message = "Website is down"
    bot.send_message(CHAT_ID, message)
    sleep(5)