from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import random, math
from .qualis_chat import ChatQualisBot



chat_bot = ChatQualisBot()


def format_search(data, mid, event, index=0):
    text = ""
    N = len(data)
    last = index + 5 if index + 5 <= N else N
    text = "*Resultados encontrados*:\n"
    for i in range(index, last):
        text += f"{data[i]}\n\n"
        # if (i < last - 1):
        #     text += "---\n"

    if N < 5:
        return text, None

    current = index

    prev_button = current - 5
    next_button = current + 5
    
    if current <= 0:
        prev_button = N - 5 
    elif current + 5 >= N:
        next_button = 0        

    keyboard = [[InlineKeyboardButton("Prev", callback_data=f"{mid}_{event}_{prev_button}"),
                 InlineKeyboardButton(f"{math.ceil(current/5) + 1}/{math.ceil(N/5)}", callback_data='nothing'),
                 InlineKeyboardButton("Next", callback_data=f"{mid}_{event}_{next_button}")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup

def get_answer(mid, user_data, index=0):
    # realizar consulta
    results = chat_bot.get_answer(user_data["text"])
    text = "Nenhum resultado encontrado."
    suggestions = None
    if results:
        text, reply_markup = format_search(results, mid, "quadriênio", index)
        return text, reply_markup, suggestions
    return text, None, None
        
    