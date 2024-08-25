from aiogram import types

def main_menu() -> types.ReplyKeyboardMarkup:
    kb = [
        [
            types.KeyboardButton(text="Поиск"),
            types.KeyboardButton(text="Мои контакты"),
        ],
        [
            types.KeyboardButton(text="Профиль"),
        ],
        
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие",
    )
    return keyboard