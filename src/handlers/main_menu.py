from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from ..lexicon.lexicon_ru import LEXICON_RU
from ..keyboards.keyboards import main_menu
from src.models.user_models import create_user
# imoprt magic filter
router: Router = Router(name=__name__)

@router.message(F.text == "/start")
async def start(message: Message):
    create_user(message.from_user.id, message.from_user.username)
    await message.answer(text=LEXICON_RU['/start'], reply_markup=main_menu())