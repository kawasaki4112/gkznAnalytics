from typing import Callable, Any, Dict, Union
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from src.utils.misc.bot_logging import bot_logger


class ErrorLoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Any],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            bot_logger.exception(f"❌ Ошибка в хэндлере {getattr(handler, '__name__', repr(handler))}", exc_info=e)
            message = data.get("message")
            if message:
                await message.answer("Произошла ошибка, попробуйте чуть позже.")

