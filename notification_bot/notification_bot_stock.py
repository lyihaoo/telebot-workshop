import os
from time import sleep
from dotenv import load_dotenv
import yfinance as yf

from telegram import Bot

load_dotenv("../.env")
TOKEN = os.getenv("token")
CHAT_ID = os.getenv("chat_id")
TICKER = "MSFT"

bot = Bot(TOKEN)

while(True):
    ticker = yf.Ticker(TICKER)
    message = "The current stock price of {} is {}".format(TICKER, ticker.info["currentPrice"])
    bot.send_message(CHAT_ID, message)
    sleep(5)