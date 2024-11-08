import datetime
from aiogram import Router
import random

router: Router = Router(name=__name__)

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from src.states.states import ChatStates
from src.keyboards.keyboards import select_liked_users
from src.models.user_models import send_like
MAX_USERS = 2
CHAT_DURATION = 15  # 10 minutes in seconds

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
    
    # Проверка, находится ли пользователь уже в комнате
    for room in chat_rooms.values():
        if user_id in room['users']:
            await callback.answer("Вы уже находитесь в комнате. Сначала выйдите из текущей комнаты.")
            return
    
    for room_id, room in chat_rooms.items():
        if len(room['users']) < MAX_USERS:
            emoji = random.choice([e for e in ANIMAL_EMOJIS if e not in room['emojis'].values()])
            room['users'].append(user_id)
            room['emojis'][user_id] = emoji
            await state.set_state(ChatStates.waiting)
            await state.update_data(room_id=room_id, emoji=emoji)
            kb = InlineKeyboardBuilder()
            kb.button(text="Выйти из комнаты", callback_data=f"leave_room:{room_id}")
            await callback.message.edit_text(f"Вы добавлены в комнату {room_id}. Ваш аватар: {emoji}. Ожидайте начала чата.", reply_markup=kb.as_markup())
            
            if len(room['users']) == MAX_USERS:
                await start_chat(room_id, callback, state)
            return

    new_room_id = len(chat_rooms) + 1
    emoji = random.choice(ANIMAL_EMOJIS)
    chat_rooms[new_room_id] = {'users': [user_id], 'messages': [], 'emojis': {user_id: emoji}}
    await state.set_state(ChatStates.waiting)
    await state.update_data(room_id=new_room_id, emoji=emoji)
    kb = InlineKeyboardBuilder()
    kb.button(text="Выйти из комнаты", callback_data=f"leave_room:{new_room_id}")
    await callback.message.edit_text(f"Вы добавлены в новую комнату {new_room_id}. Ваш аватар: {emoji}. Ожидайте других участников.", reply_markup=kb.as_markup())

@router.callback_query(F.data.startswith("leave_room:"))
async def leave_room(callback: types.CallbackQuery, state: FSMContext):
    room_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id
    
    if room_id in chat_rooms and user_id in chat_rooms[room_id]['users']:
        chat_rooms[room_id]['users'].remove(user_id)
        del chat_rooms[room_id]['emojis'][user_id]
        
        if len(chat_rooms[room_id]['users']) == 0:
            del chat_rooms[room_id]
        
        await state.clear()
        # TODO Добавить выход из чата, когда он начался (через /start)
        await callback.message.edit_text('Вы вышли из комнаты. Нажмите "Поиск", чтобы начать заново.')
    else:
        await callback.answer("Ошибка: комната не найдена или вы не состоите в ней.")

async def start_chat(room_id, callback, state):
    room = chat_rooms[room_id]

    for user_id in room['users']:
        user_state = FSMContext(state.storage, user_id)
        await user_state.set_state(ChatStates.chatting)

        await user_state.update_data(room_id=room_id)
        await callback.bot.send_message(user_id, "Чат начался! У вас есть 10 минут для общения. Чтобы выйти из чата, нажмите /start")

    await asyncio.sleep(CHAT_DURATION)
    for user_id in room['users']:
        user_state = FSMContext(state.storage, user_id)
        await user_state.clear()
        # TODO Сделать лайки
    for user_id in room['users']:
        emojis = {uid: room['emojis'][uid] for uid in room['users'] if uid != user_id}
        await callback.bot.send_message(user_id, "Время чата истекло. Пора ставить лайки!", reply_markup=select_liked_users(emojis))    
    del chat_rooms[room_id]

@router.message()
async def handle_chat_message(message: types.Message, state: FSMContext):
    # TODO Сделать кастомный фильтр
    state = FSMContext(state.storage, message.from_user.id)

    if await state.get_state() == ChatStates.chatting:
        data = await state.get_data()

        room_id = data['room_id']
        if not chat_rooms:
            return
        room = chat_rooms[room_id]
        
        sender_emoji = room['emojis'][message.from_user.id]

        for user_id in room['users']:
            if user_id != message.from_user.id:
                # TODO Собирать сообщения в базу даныных для анализа нарушений
                await message.bot.send_message(user_id, f"{sender_emoji}: \n {message.text}")

        room['messages'].append((message.from_user.id, message.text))

@router.callback_query(lambda c: c.data.startswith('like:'))
async def handle_like(callback: types.CallbackQuery, state: FSMContext):
    liked_user_id = int(callback.data.split(':')[1])
    from_user_id = callback.from_user.id
    
    # Проверяем, не ставит ли пользователь лайк сам себе
    if liked_user_id == from_user_id:
        await callback.answer("Вы не можете поставить лайк самому себе!")
        return
    send_like_success  = send_like(from_user_id, liked_user_id)
    if send_like_success:
        await callback.answer("Лайк успешно поставлен!")
        # Отправляем уведомление пользователю, получившему лайк
        await callback.bot.send_message(
            liked_user_id,
            "Вам поставили лайк! Переходите в профиль и проверяйте, кто вас лайкнул!"
        )
    else:
        await callback.answer("Вы уже поставили лайк этому пользователю или лайки на сегодня закончились!")
    
    
