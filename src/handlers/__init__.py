__all__ = ("router",)

from aiogram import Router

from .chat import router as chat_router
from .contacts import router as contacts_router
from .profile import router as profile_router
from .main_menu import router as main_menu_router

router = Router(name=__name__)

router.include_routers(
    main_menu_router,
    profile_router,
    contacts_router,
    chat_router,
)

# this one has to be the last!
