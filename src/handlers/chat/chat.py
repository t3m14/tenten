from aiogram import Router
import random

router: Router = Router(name=__name__)

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from src.states.states import ChatStates

MAX_USERS = 2
CHAT_DURATION = 600  # 10 minutes in seconds

#TODO Вынести в базу данных
chat_rooms = {}

ANIMAL_EMOJIS = ['🐶', '🐱', '🐭', '🐹', '🐰', '🦊', '🐻', '🐼', '🐨', '🐯']

@router.message(F.text == "Поиск")
async def cmd_start(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="Поиск комнаты", callback_data="search_room")
    await message.answer("Добро пожаловать! Нажмите кнопку для поиска комнаты.", reply_markup=kb.as_markup())

@router.callback_query(F.data == "search_room")
async def search_room(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    
    for room_id, room in chat_rooms.items():
        if len(room['users']) < MAX_USERS:
            emoji = random.choice([e for e in ANIMAL_EMOJIS if e not in room['emojis'].values()])
            room['users'].append(user_id)
            room['emojis'][user_id] = emoji
            await state.set_state(ChatStates.waiting)
            await state.update_data(room_id=room_id, emoji=emoji)
            await callback.message.edit_text(f"Вы добавлены в комнату {room_id}. Ваш аватар: {emoji}. Ожидайте начала чата.")
            
            if len(room['users']) == MAX_USERS:
                await start_chat(room_id, callback, state)
            return

    new_room_id = len(chat_rooms) + 1
    emoji = random.choice(ANIMAL_EMOJIS)
    chat_rooms[new_room_id] = {'users': [user_id], 'messages': [], 'emojis': {user_id: emoji}}
    await state.set_state(ChatStates.waiting)
    await state.update_data(room_id=new_room_id, emoji=emoji)
    await callback.message.edit_text(f"Вы добавлены в новую комнату {new_room_id}. Ваш эмодзи: {emoji}. Ожидайте других участников.")

async def start_chat(room_id, callback, state):
    room = chat_rooms[room_id]

    for user_id in room['users']:
        user_state = FSMContext(state.storage, user_id)
        await user_state.set_state(ChatStates.chatting)

        await user_state.update_data(room_id=room_id)
        await callback.bot.send_message(user_id, "Чат начался! У вас есть 10 минут для общения.")

    await asyncio.sleep(CHAT_DURATION)
    
    for user_id in room['users']:
        # TODO Сделать лайки
        await callback.bot.send_message(user_id, "Время чата истекло. Вы возвращены в главное меню.")
        await cmd_start(types.Message(chat=types.Chat(id=user_id, type="private")))
    
    del chat_rooms[room_id]

@router.message()
async def handle_chat_message(message: types.Message, state: FSMContext):
    # TODO Сделать кастомный фильтр
    state = FSMContext(state.storage, message.from_user.id)

    if await state.get_state() == ChatStates.chatting:
        data = await state.get_data()

        room_id = data['room_id']
        room = chat_rooms[room_id]
        sender_emoji = room['emojis'][message.from_user.id]

        for user_id in room['users']:
            if user_id != message.from_user.id:
                # TODO Собирать сообщения в базу даныных для анализа нарушений
                await message.bot.send_message(user_id, f"{sender_emoji}: \n {message.text}")

        room['messages'].append((message.from_user.id, message.text))