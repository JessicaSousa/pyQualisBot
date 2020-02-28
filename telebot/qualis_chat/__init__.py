
from .rasa import ChatQualisBot


def welcome_message(user_id, context):
    if context.user_data:
        event = context.user_data[user_id]["event"]
        text = "Olá novamente, atualmente você pode realizar consultas "\
               "de periódicos do evento de classificação referente ao último "\
                f"{event}. Para consultar a ajuda use o comando /help a qualquer"\
                " momento."
    else:
        context.user_data[user_id] ={
            "event":"quadriênio"
        }  
        
        text = ("Este bot tem como objetivo facilitar a consulta de qualis de "
        "periódicos. As informações aqui disponíves são retiradas "
        "diretamente da [Plataforma Sucupira](https://sucupira.capes.gov.br/"
        "sucupira/public/consultas/coleta/veiculoPublicacaoQualis/"
        "listaConsultaGeralPeriodicos.jsf). As consultas são realizadas "
        "por padrão utlizando o evento de classificação do *quadriênio "
        "2013-2016*, para mudar para o triênio use o comando /event. "
        "Para saber mais informações sobre o bot use o comando /help.")

    return text


def get_user_data(text, context_user_data):
    event = context_user_data["event"]
    user_data = {
        "event": event,
        "text": text
    }
    return user_data


def update_user_data(selected, chat_id, context):
    if selected == "quadriênio" or selected == "triênio":
        context.user_data[chat_id]["event"] = selected
        return True
    return False