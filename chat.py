from telegram import InlineKeyboardMarkup, InlineKeyboardButton
import random, math
from pyQualis import Search


search = Search()

def format_search(data, mid, event, index=0):
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

    keyboard = [[InlineKeyboardButton("Prev", callback_data=f"{mid}_{event}_{prev_button}"),
                 InlineKeyboardButton(f"{math.ceil(current/5) + 1}/{math.ceil(N/5)}", callback_data='nothing'),
                 InlineKeyboardButton("Next", callback_data=f"{mid}_{event}_{next_button}")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    return text, reply_markup



def get_answer(mid, user_data, index=0):
    # realizar consulta
    results = search.by_area(user_data["text"])
    if results.empty:
        return "Nenhum resultado encontrado.", None
    else:
        return format_search(results, mid, user_data["event"], index)
        
    