from aiogram import F, Router,  types

router: Router = Router(name=__name__)

@router.message(F.text == "Профиль")
async def profile(message: types.Message):
    await message.answer(text="Профиль")