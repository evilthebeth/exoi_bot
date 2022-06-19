#!/usr/bin/env python
# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
from multiprocessing import connection
import sqlite3
from telegram import __version__ as TG_VER

try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, CallbackQueryHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

    connection = sqlite3.connect("../db/db.sqlite")
    cursor = connection.cursor()
    SQL = """INSERT INTO astra(user_id,text) VALUES({},'{}')""".format(update.message.chat.id,update.message.text)
    print(update.message.text)
    cursor.execute(SQL)

    row_id = str(cursor.lastrowid)

    keyboard = [
    [
        InlineKeyboardButton("Daily", callback_data='0 ' + row_id),
        InlineKeyboardButton("Random", callback_data='1 ' + row_id),
        InlineKeyboardButton("TBA", callback_data='3 ' + row_id)
    ]
]
    reply_markup = InlineKeyboardMarkup(keyboard)

    
    await update.message.reply_text("last row ID: {}".format(row_id),reply_markup=reply_markup)
    print(update)
    connection.commit()
    connection.close()

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()


    freq = query.data.split()[0]
    row_id = query.data.split()[1]

    connection = sqlite3.connect("../db/db.sqlite")
    cursor = connection.cursor()

    SQL = "UPDATE astra SET frequency='{}' where id={}".format(freq,row_id)

    
    cursor.execute(SQL)
    connection.commit()
    connection.close()

    await query.edit_message_text(text=f"Frequency set to: {query.data}")

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    f = open("../cfg/tkn","r")
    tkn = f.readline().rstrip()
    application = Application.builder().token(tkn).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    application.add_handler(CallbackQueryHandler(button))
    

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
