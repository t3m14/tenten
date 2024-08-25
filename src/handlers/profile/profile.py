from aiogram import F, Router,  types
from src.keyboards.keyboards import pay_subscribe
router: Router = Router(name=__name__)

@router.message(F.text == "Профиль")
async def profile(message: types.Message):
    likes = 0
    sub = 0
    # TODO Сделать базу данных для пользователей
    # TODO Сделать получение информации
    # TODO Вынести текст в lexicon
    await message.answer(text=f"""
                        Ваш профиль
                        Статус вашей подписки {sub}
                        Осталось лайков {likes}
                        """, reply_markup=pay_subscribe())