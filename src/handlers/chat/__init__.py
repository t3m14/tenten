from aiogram import Router
from .chat import router as chat_router

router: Router = Router(name=__name__)

router.include_router(chat_router)