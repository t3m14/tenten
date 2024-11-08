from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

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

def pay_subscribe() -> types.InlineKeyboardMarkup:
    kb = [
        #TODO Реализовать оплату звездочками
        [types.InlineKeyboardButton(text='Оплатить подписку на месяц', callback_data="pay")]    
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=kb)

def select_liked_users(emojis):
    print(emojis)
    for user_id, emoji in emojis.items():
        # item['emojis']
        likes_keyboard = InlineKeyboardBuilder()
        likes_keyboard.button(text=str(emoji), callback_data=f"like:{str(user_id)}")
        likes_keyboard.row()
    return likes_keyboard.as_markup()
