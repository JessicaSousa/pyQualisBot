class Strings:
    FIRST_START_MESSAGE = (
        "Este bot tem como objetivo facilitar a consulta de qualis de "
        "periódicos. As informações aqui disponíves são retiradas "
        "diretamente da [Plataforma Sucupira](https://sucupira.capes.gov.br/"
        "sucupira/public/consultas/coleta/veiculoPublicacaoQualis/"
        "listaConsultaGeralPeriodicos.jsf). As consultas são realizadas "
        "por padrão utlizando o evento de classificação do *quadriênio "
        "2013-2016*, para mudar para o triênio use o comando /event. "
        "Para saber mais informações sobre o bot use o comando /help."
    )

    HELP_MESSAGE = (
        "Para selecionar o evento de classificação use o comando /event.\n"
        "Consultas podem ser feitas apenas colocando o nome da área desejada."
    )

    QUADRIEN = "PERIÓDICOS QUADRIÊNIO 2013-2016"

    TRIEN = "PERIÓDICOS TRIÊNIO 2010-2012"

    EVENT_SELECT = "Selecione o evento de classificação desejado:"