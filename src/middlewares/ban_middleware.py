from typing import Callable, Dict, Any, Union
from aiogram import BaseMiddleware
from aiogram.types import User, Message, CallbackQuery

from src.data.repositories.user_repository import user_crud


class BanCheckMiddleware(BaseMiddleware):
    text = "❌ Вы забанены и не можете пользоваться ботом."

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Any],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        this_user: User = data.get("event_from_user")

        user_ = await user_crud.get(tg_id=this_user.id)
        if not user_:
            return await handler(event, data)

        if user_.role == "banned":

            if isinstance(event, Message):
                await event.answer(self.text)
            else:
                await event.answer(self.text, show_alert=True)
            return
        
        return await handler(event, data)
