import logging
import os

from telebot.chat import get_answer
from telebot.strings import Strings

from . import qualis_chat

from telegram import InlineKeyboardButton, InlineKeyboardMarkup 
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler, PicklePersistence)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    user = update.message.from_user
    text = qualis_chat.welcome_message(user.id, context)
    update.message.reply_text(text, parse_mode='markdown')


# Evento (qualis_chat)
def event(update, context):
    keyboard = [[InlineKeyboardButton(Strings.QUADRIEN, callback_data="quadriênio")],
                [InlineKeyboardButton(Strings.TRIEN, callback_data="triênio")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(Strings.EVENT_SELECT, reply_markup=reply_markup)

 
def reply_user(update, context):
    """Echo the user message."""
    user = update.message.from_user
    logger.info("[%s] %s says: %s",user.id, user.first_name, update.message.text)

    user_data = qualis_chat.get_user_data(update.message.text, context.user_data[user.id])
    context.user_data[user.id][update.message.message_id] = user_data

    # Obtém o texto, opções e sugestões
    text, options, suggestions = get_answer(mid = update.message.message_id, user_data = user_data)
    reply_markup = InlineKeyboardMarkup(options)
    update.message.reply_text(text, reply_markup=reply_markup, parse_mode="markdown")
    if suggestions:
        print("okay")


def button_check_answer(query, context=None):
    selected = query.data
    reply_markup = query.message.reply_markup

    if "v2" not in selected:
        mid, value = selected.split("_")

        query.answer("Pressione novamente para confirmar a sua escolha.")
        right_callback = f"{mid}_correto"
        wrong_callback = f"{mid}_errado"

        if value == "correto":
            right_callback += "_v2"
        else:
            wrong_callback += "_v2"

        keyboard = [[InlineKeyboardButton("Certo ✔️", callback_data=right_callback),
                     InlineKeyboardButton("Errado ❌", callback_data=wrong_callback)
        ]]
    else:
        mid, value, _ = selected.split("_")
        query.answer(f"O resultado foi marcado como {value}.")
        keyboard = []
        cid = query.message.chat.id
        context.user_data[cid][int(mid)]['check'] = value

    # Retorna o inline keyboard atualizado
    inline_keyboards = iter(reply_markup['inline_keyboard'])
    next(inline_keyboards)
    for inline_keyboard in inline_keyboards:
        keyboard.append(inline_keyboard)
    query.edit_message_reply_markup(reply_markup=InlineKeyboardMarkup(keyboard))

 
def button(update, context):
    query = update.callback_query
    selected = query.data
    cid = query.message.chat.id
    logger.info("[%s] %s pressed: %s",cid, query.message.chat.first_name, selected)

    is_updated = qualis_chat.update_user_data(selected, cid, context)

    # query.answer(f"Clicado: {selected}")

    if selected == "nothing":
        query.answer("Este botão não faz nada 😅.")
    elif is_updated is True:
        query.edit_message_text(f"Opção selecionada: {selected}")
    elif "correto" in selected or "errado" in selected:
        button_check_answer(query, context)
    else:
        mid, _, index = selected.split("_")
        user_data = context.user_data[cid][int(mid)]
        text, keyboard, suggestions = get_answer(mid, user_data, int(index))
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')
        if suggestions:
            print("Sugestões")

    #query.answer(f"Selecionada a opção: {selected}")


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
    updater.dispatcher.add_handler(CommandHandler('event', event)) # handler utilizado pelo qualis_chat
    updater.dispatcher.add_handler(MessageHandler(Filters.text, reply_user))
    updater.dispatcher.add_error_handler(error)
 
    # Start the Bot
    updater.start_polling()
 
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
 
 
if __name__ == '__main__':
    init()