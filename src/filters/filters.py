from aiogram.filters import Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from src.states.states import ChatStates
class ChatFilter(Filter):
    async def __call__(self, message: Message, state: FSMContext) -> bool:
        return await state.get_state() == ChatStates.chatting        