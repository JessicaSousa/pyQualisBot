import logging
import os

from telebot.chat import get_answer
from telebot.strings import Strings

from telegram import InlineKeyboardButton, InlineKeyboardMarkup 
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler, PicklePersistence)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    user = update.message.from_user
    if context.user_data:
        event = context.user_data[user.id]["event"]
        update.message.reply_text(
            "Olá novamente, atualmente você pode realizar consultas "\
            "de periódicos do evento de classificação referente ao último "\
            f"{event}. Para consultar a ajuda use o comando /help a qualquer"\
            " momento.")
    else:
        context.user_data[user.id] ={
            "event":"quadriênio"
        }  
        update.message.reply_text(Strings.FIRST_START_MESSAGE, parse_mode='markdown')


def event(update, context):
    keyboard = [[InlineKeyboardButton("PERIÓDICOS QUADRIÊNIO 2013-2016", 
                                       callback_data="quadriênio")],
                 [InlineKeyboardButton("PERIÓDICOS TRIÊNIO 2010-2012", 
                                      callback_data="triênio")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Selecione o evento de classificação desejado:", 
                              reply_markup=reply_markup)

 
def reply_user(update, context):
    """Echo the user message."""
    user = update.message.from_user
    logger.info("[%s] %s says: %s",user.id, user.first_name, update.message.text)
    
    event = context.user_data[user.id]["event"]
    user_data = {
        "event": event,
        "text": update.message.text
    }
    context.user_data[user.id][update.message.message_id] = user_data
    # Obtém o texto, opções e sugestões
    text, options, suggestions = get_answer(mid = update.message.message_id, user_data = user_data)
    update.message.reply_text(text, reply_markup=options, parse_mode="markdown")
    if suggestions:
        print("okay")

 
def button(update, context):
    query = update.callback_query
    selected = query.data
    cid = query.message.chat.id
    logger.info("[%s] %s pressed: %s",cid, query.message.chat.first_name, selected)
    if selected == "nothing":
        query.answer("Esse botão não faz nada.")
    elif(selected == "quadriênio" or selected == "triênio"):
        context.user_data[cid]["event"] = selected
        query.edit_message_text(f"Evento selecionado: {selected}")
    else:
        mid, _, index = selected.split("_")
        user_data = context.user_data[cid][int(mid)]
        text, reply_markup = get_answer(mid, user_data, int(index))
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')

    query.answer(f"Selecionada a opção: {selected}")


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def help(update, context):
    user = update.message.from_user
    logger.info("[%s] %s called help command.", user.id, user.first_name)
    update.message.reply_text(Strings.HELP_MESSAGE)


def init():
    logger.info("Starting bot")
    # Create the Updater and pass it your bot's token.
    pp = PicklePersistence(filename='conversationbot')
    updater = Updater(os.getenv("TOKEN"), persistence=pp, use_context=True)
    
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_handler(CommandHandler('event', event))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, reply_user))
    updater.dispatcher.add_error_handler(error)
 
    # Start the Bot
    updater.start_polling()
 
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
 
 
if __name__ == '__main__':
    init()