from aiogram import Router
from .contacts import router as contacts_routers

router: Router = Router(name=__name__)

router.include_router(contacts_routers)