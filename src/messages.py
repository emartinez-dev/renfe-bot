"""This module contains the messages that the bot sends to the user"""

user_messages = {
    "welcome": "Hola {}. Bienvenido a tu bot de Renfe. Te ayudaré a encontrar billetes de tren para tus viajes. Para empezar, escribe /ayuda para ver los comandos disponibles.",
    "help": "/ayuda - Muestra los comandos disponibles\n/buscar - Busca billetes de tren\n/reintentar - Vuelve a lanzar la última búsqueda\n/cancelar - Cancela la búsqueda en curso.",
    "cancel": "La búsuqueda ha sido cancelada.",
    "cancel_params": "Reiniciando el proceso de búsqueda, usa /buscar para empezar de nuevo",
    "search_already_running": "Ya hay una búsqueda en curso, por favor espera o utiliza /cancelar para cancelarla",
    "start": "🚉 ¿Desde qué estación sales?",
    "destination": "🚉 ¿A qué estación vas?",
    "station_invalid": "Por favor, introduce el nombre de una estación válida.",
    "destination_date": "📅 ¿Qué día y a partir de qué hora sales?",
    "return_date": "📅 ¿Qué día y a partir de qué hora vuelves?",
    "needs_return": "🔙 ¿Necesitas billete de vuelta?",
    "needs_filter": "🔍 ¿Quieres filtrar los resultados (precio, duración)?",
    "max_price": "💵 ¿Precio máximo? (introduce 0 si no quieres filtrar por precio)",
    "max_duration": "⏳ ¿Duración máxima? (introduce 0 si no quieres filtrar por duración)",
    "searching": "🔎 Buscando billetes...",
    "station_not_found": "No he encontrado la estación {}, pero he encontrado estas:\n{}\nPor favor, introduce la tuya de nuevo.",
    "wrong_date": "La fecha es incorrecta, introdúcela de nuevo.",
    "wrong_number": "Número incorrecto, introdúcelo de nuevo.",
}
