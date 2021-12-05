import os
from dotenv import load_dotenv

from telegram import Bot

load_dotenv("../.env")
TOKEN = os.getenv("token")
CHAT_ID = os.getenv("chat_id")

