from datetime import datetime, timezone

def format_time(ms):
    """
    Formata um valor em milissegundos para o formato de tempo hh:mm:ss.

    Parâmetros:
    ms (int): O valor em milissegundos a ser convertido.

    Retorna:
    str: O tempo formatado no formato "hh:mm:ss".
    """
    
    seconds = ms / 1000.0
    return datetime.fromtimestamp(seconds, timezone.utc).strftime('%H:%M:%S')