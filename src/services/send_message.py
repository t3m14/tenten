from bot import Bot

def send_message(bot: Bot, chat_id: int, message: str):
    bot.send_message(chat_id, message)