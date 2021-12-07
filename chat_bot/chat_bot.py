import os
import logging
from uuid import uuid4
from dotenv import load_dotenv
import yfinance as yf

from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler, InlineQueryHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

load_dotenv("../.env")
TOKEN = os.getenv("token")
CHAT_ID = os.getenv("chat_id")
TICKER = "MSFT"

def get_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        message = "The current stock price of {} is {}".format(symbol.upper(), ticker.info["currentPrice"]) 
    except:
        message = "The Symbol {} is not found".format(symbol.upper())
    
    return message

def error(update:Update, context: CallbackContext):
    '''Log Errors caused by Updates'''
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def show(update: Update, context: CallbackContext):
    update.message.reply_text(get_price(TICKER))

def check_stock(update: Update, context: CallbackContext):
    symbol = update.message.text.replace("!", "").strip()
    update.message.reply_text(get_price(symbol))

def stock_info(update: Update, context: CallbackContext):
    update.message.reply_text("Please enter the stock symbol or use /cancel to cancel the request.")
    return 1

def get_stock(update: Update, context: CallbackContext):
    symbol = update.message.text.strip()
    ticker = yf.Ticker(symbol).info
    if 'symbol' not in ticker:
        update.message.reply_text("The Symbol {} is not found.\n\nPlease enter a new stock symbol or use /cancel to cancel the request.".format(symbol.upper()))
        return 1
    
    context.chat_data["ticker"] = ticker
        
    # revenuePerShare, dividendYield, dayHigh, dayLow
    keyboard = [
        [
            InlineKeyboardButton('Revenue Per Share', callback_data = "rps"),
            InlineKeyboardButton("Dividend Yield", callback_data= "divYield")
        ],
        [
            InlineKeyboardButton("Day High", callback_data="high"),
            InlineKeyboardButton("Day Low", callback_data="low")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Press the button for the relevant information for {}".format(symbol.upper()), reply_markup = reply_markup)

    return 2

def rps(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    ticker = context.chat_data['ticker']
    message = "The Revenue Per Share for {} is ${}".format(ticker["symbol"], ticker['revenuePerShare'])
    keyboard = [
        [
            InlineKeyboardButton("Dividend Yield", callback_data= "divYield")
        ],
        [
            InlineKeyboardButton("Day High", callback_data="high"),
            InlineKeyboardButton("Day Low", callback_data="low")
        ],
        [
            InlineKeyboardButton('End', callback_data = "end"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text=message, reply_markup=reply_markup)
    return 2

def div(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    ticker = context.chat_data['ticker']
    message = "The Dividend Yield for {} is ${}".format(ticker["symbol"], ticker['dividendYield'])
    keyboard = [
        [
            InlineKeyboardButton("Revenue Per Share", callback_data= "rps")
        ],
        [
            InlineKeyboardButton("Day High", callback_data="high"),
            InlineKeyboardButton("Day Low", callback_data="low")
        ],
        [
            InlineKeyboardButton('End', callback_data = "end"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text=message, reply_markup=reply_markup)
    return 2

def high(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    ticker = context.chat_data['ticker']
    message = "The Day High for {} is ${}".format(ticker["symbol"], ticker['dayHigh'])
    keyboard = [
        [
            InlineKeyboardButton("Revenue Per Share", callback_data= "rps"),
            InlineKeyboardButton("Dividend Yield", callback_data= "divYield")
        ],
        [
            InlineKeyboardButton("Day Low", callback_data="low")
        ],
        [
            InlineKeyboardButton('End', callback_data = "end"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text=message, reply_markup=reply_markup)
    return 2

def low(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    ticker = context.chat_data['ticker']
    message = "The Day Low for {} is ${}".format(ticker["symbol"], ticker['dayLow'])
    keyboard = [
        [
            InlineKeyboardButton("Revenue Per Share", callback_data= "rps"),
            InlineKeyboardButton("Dividend Yield", callback_data= "divYield")
        ],
        [
            InlineKeyboardButton("Day High", callback_data="high")
        ],
        [
            InlineKeyboardButton('End', callback_data = "end"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    query.edit_message_text(text=message, reply_markup=reply_markup)
    return 2

def end(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    context.chat_data['ticker'] = None

    query.edit_message_text(text="Conversation Ended")
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext):
    update.message.reply_text("Request Cancelled")

    return ConversationHandler.END

def inline_price(update: Update, context: CallbackContext):
    symbol = update.inline_query["query"]
    message = get_price(symbol)
    results = [
        InlineQueryResultArticle(
            id = uuid4(),
            title = "Price of {}".format(symbol.upper()),
            input_message_content= InputTextMessageContent(message)
        )
    ]

    update.inline_query.answer(results)

def main():
    '''Function to start the bot'''
    # Create the Updater and pass it your bot's token
    updater = Updater(TOKEN, use_context=True)

    # Get dispatcher to register handlers
    dp = updater.dispatcher

    stock_info_conv = ConversationHandler(
        entry_points=[CommandHandler('stock_info', stock_info)],
        states = {
            1: [
                MessageHandler(Filters.text, get_stock)
            ],
            2:[
                CallbackQueryHandler(rps, pattern="rps"),
                CallbackQueryHandler(div, pattern="divYield"),
                CallbackQueryHandler(high, pattern="high"),
                CallbackQueryHandler(low, pattern="low"),
                CallbackQueryHandler(end, pattern="end")
            ]
        },
        fallbacks = [CommandHandler('cancel', cancel)],
        allow_reentry= True
    )

    dp.add_handler(CommandHandler('show', show))
    dp.add_handler(MessageHandler(Filters.regex("^!"), check_stock))
    dp.add_handler(stock_info_conv)
    dp.add_handler(InlineQueryHandler(inline_price))

    dp.add_error_handler(error)
    
    # Start the bot
    updater.start_polling()

    # run the bot until interrupted (e.g. using Ctrl + c)
    updater.idle()


if __name__ == '__main__':
    main()