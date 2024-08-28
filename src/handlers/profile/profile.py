from aiogram import F, Router, types
from src.keyboards.keyboards import pay_subscribe
from src.models.user_models import *

router: Router = Router(name=__name__)

@router.message(F.text == "Профиль")
async def profile(message: types.Message):
    user_id = message.from_user.id
    info = get_user_info(user_id)

    if info:
        subscription_status = "Активна" if info["subscription_status"] else "Неактивна"
        await message.answer(text=f"Ваш профиль\nСтатус вашей подписки: {subscription_status}\nКоличество лайков: {info['likes_count']}", reply_markup=pay_subscribe())
    else:
        await message.answer(text="Профиль не найден.", reply_markup=pay_subscribe())