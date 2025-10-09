from aiogram import Dispatcher, F

from src.routers.router import router


def register_all_routers(dp: Dispatcher):
    dp.message.filter(F.chat.type == "private")
    dp.callback_query.filter(F.message.chat.type == "private")

    dp.include_router(router)
