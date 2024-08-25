from aiogram import Router
from .profile import router as profile_router

router: Router = Router(name=__name__)

router.include_router(profile_router)