from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import random, math
from .qualis_chat import ChatQualisBot

chat_bot = ChatQualisBot()


def format_search(data, mid, event, user_data, index=0):
    text = ""
    N = len(data)
    last = index + 5 if index + 5 <= N else N
    text = "*Resultados encontrados*:\n"
    keyboard = []
    for i in range(index, last):
        text += f"{data[i]}\n\n"
        # if (i < last - 1):
        #     text += "---\n"

    if "check" not in user_data:
        keyboard.append([InlineKeyboardButton("Certo ✔️", callback_data=f"{mid}_correto"),
                         InlineKeyboardButton("Errado ❌", callback_data=f"{mid}_errado")])

    if N <= 5:
        return text, keyboard

    current = index

    prev_button = current - 5
    next_button = current + 5
    
    if current <= 0:
        prev_button = N - 5 
    elif current + 5 >= N:
        next_button = 0        

    keyboard.append([InlineKeyboardButton("⬅️", callback_data=f"{mid}_{event}_{prev_button}"),
                 InlineKeyboardButton(f"{math.ceil(current/5) + 1}/{math.ceil(N/5)}", callback_data='nothing'),
                 InlineKeyboardButton("➡️", callback_data=f"{mid}_{event}_{next_button}")])

    #reply_markup = InlineKeyboardMarkup(keyboard)
    return text, keyboard

def get_answer(mid, user_data, index=0):
    # realizar consulta
    status,results = chat_bot.get_answer(user_data["text"])
    text = "Nenhum resultado encontrado."
    
    if(status == 1):
        text = 'O termo não foi entendido'
        #futuramente sugestao
    if(status == 0):
        suggestions = None
        if results:
            text, reply_markup = format_search(results, mid, "quadriênio", user_data, index)
            return text, reply_markup, suggestions
    return text, None, None
        
    