import logging
import os
import settings
from pyQualis import Search

import math

 
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

search = Search()

def format_search(data, field, value, event, index=0):
    text = ""
    N = data.shape[0]
    last = index + 5 if index + 5 <= N else N
    for i in range(index, last):
        text += f"*ISSN*: {data.iloc[i, 0]}\n"
        text += f"*Título*: {data.iloc[i, 1]}\n"
        text += f"*Área de Avaliação*:\n{data.iloc[i, 2]}\n"
        text += f"*Classificação*: {data.iloc[i, 3]}\n"
        text += "===============================\n"

    current = index

    prev_button = current - 5
    next_button = current + 5
    
    if current <= 0:
        prev_button = N - 5 
    elif current + 5 >= N:
        next_button = 0        

    keyboard = [[InlineKeyboardButton("Prev", callback_data=f"{field}_{value}_{event}_{prev_button}"),
                 InlineKeyboardButton(f"{math.ceil(current/5) + 1}/{math.ceil(N/5)}", callback_data='nothing'),
                 InlineKeyboardButton("Next", callback_data=f"{field}_{value}_{event}_{next_button}")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup

def start(update, context):
    context.chat_data["event"] = "quadriênio"
    update.message.reply_text(
        "Este bot tem como objetivo facilitar a consulta de qualis de "\
        "periódicos. As informações aqui disponíves são retiradas "\
        "diretamente da [Plataforma Sucupira](https://sucupira.capes.gov.br/"\
        "sucupira/public/consultas/coleta/veiculoPublicacaoQualis/"\
        "listaConsultaGeralPeriodicos.jsf). As consultas são realizadas "\
        "por padrão utlizando o evento de classificação do *quadriênio "\
        "2013-2016*, para mudar para o triênio use o comando /event. "\
        "Para saber mais informações sobre o bot use o comando /help.",
        parse_mode='markdown'
    )
 

def event(update, context):
    keyboard = [[InlineKeyboardButton("PERIÓDICOS QUADRIÊNIO 2013-2016", 
                                       callback_data="quadriênio")],
                 [InlineKeyboardButton("PERIÓDICOS TRIÊNIO 2010-2012", 
                                      callback_data="triênio")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Selecione o evento de classificação desejado:", 
                              reply_markup=reply_markup)



def button(update, context):
    query = update.callback_query
    selected = query.data

    if selected == "nothing":
        query.answer("Esse botão não faz nada.")
    if selected == "quadriênio":
        context.chat_data["event"] = "quadriênio"
        query.edit_message_text(text="Selecionada a opção: {}".format(query.data))
    elif selected == "triênio":
        context.chat_data["event"] = "triênio"
        query.edit_message_text(text="Selecionada a opção: {}".format(query.data))

    current_selected = selected.split("_")
    if len(current_selected) == 4:
        field, value, event, index = selected.split("_")
        text, reply_markup = find(event, field, value,int(index))
        # text, reply_markup = format_search(results,field, value, event, int(index))
        query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode='markdown')
    
    #query.answer(f"Selecionada a opção: {selected}")



def find(event, field, value, index=0):
    if field == "area":
        results = search.by_area(value, event=event)
    elif field == "title":
        results = search.by_title(value, event=event)
    elif field == "issn":
        results = search.by_issn(value)
    elif field == "classification":
        results = search.by_classification(value, event=event)
    if results.empty:
        return "Nenhum resultado encontrado para a consulta informada.", None
    else:
        return format_search(results,field, value, event, index)



def area(update, context):
    if context.args:
        event  = context.chat_data["event"]
        text, reply_markup = find(event, "area", context.args[0])
        update.message.reply_text(text, reply_markup=reply_markup, parse_mode='markdown')
    else:
        update.message.reply_text("Você precisa informar uma área. Ex.: `/area computação`", parse_mode='markdown')


def title(update, context):
    if context.args:
        event  = context.chat_data["event"]
        text, reply_markup = find(event, "title", context.args[0])
        update.message.reply_text(text, reply_markup=reply_markup, parse_mode='markdown')
    else:
        update.message.reply_text("Você precisa informar uma título. Ex.: `/title elsevier`", parse_mode='markdown')


def issn(update, context):
    if context.args:
        event  = context.chat_data["event"]
        text, reply_markup = find(event, "issn", context.args[0])
        update.message.reply_text(text, reply_markup=reply_markup, parse_mode='markdown')
    else:
        update.message.reply_text("Você precisa informar um ISSN. Ex.: `/issn 1548-7660`", parse_mode='markdown')


def classification(update, context):
    if context.args:
        event  = context.chat_data["event"]
        text, reply_markup = find(event, "classification", context.args[0])
        update.message.reply_text(text, reply_markup=reply_markup, parse_mode='markdown')
    else:
        update.message.reply_text("Você precisa informar uma classificação. Ex.: `/classification A1`", parse_mode='markdown')


def help(update, context):
    text = """
    Consultar de acordo com a *área*:
    * /area "nome da área"
    Consultar de acordo com o *título da revista*:
    * /title elsevier
    Consultar de acorodo com o ISSN:
    * /issn 1548-7660
    Consultar de acordo com a classificação da revista:
    * /classification A1

    Além disso é possível definir o evento de classificação usando o comando /event.
    """
    update.message.reply_text(text, paser_mode = "markdown")
 
 
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
 
 
def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.getenv("TOKEN"), use_context=True)
 
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('area', area, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('title', title, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('issn', issn, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('classification', classification, pass_args=True))
    updater.dispatcher.add_handler(CommandHandler('event', event, pass_chat_data=True))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)
 
    # Start the Bot
    updater.start_polling()
 
    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()
 
 
if __name__ == '__main__':
    main()