from aiogram import Dispatcher

from src.data.db import async_session

from src.middlewares.error_logging_middleware import ErrorLoggingMiddleware
from src.middlewares.user_middleware import ExistsUserMiddleware
from src.middlewares.throttling_middleware import ThrottlingMiddleware
from src.middlewares.ban_middleware import BanCheckMiddleware


def register_all_middlwares(dp: Dispatcher):
    dp.callback_query.outer_middleware(ErrorLoggingMiddleware())
    dp.message.outer_middleware(ErrorLoggingMiddleware())

    dp.callback_query.outer_middleware(ExistsUserMiddleware())
    dp.message.outer_middleware(ExistsUserMiddleware())

    dp.callback_query.outer_middleware(ThrottlingMiddleware())
    dp.message.middleware(ThrottlingMiddleware())

    dp.callback_query.outer_middleware(BanCheckMiddleware())
    dp.message.middleware(BanCheckMiddleware())
