from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Create your states here.
class ChatStates(StatesGroup):
    waiting = State()
    chatting = State()