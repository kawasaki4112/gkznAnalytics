import os
from typing import Callable, Dict, Any, Union
from aiogram import BaseMiddleware
from aiogram.types import User, Message, CallbackQuery

from src.data.repositories.user_repository import user_crud


class AdminCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Any],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        this_user: User = data.get("event_from_user")
        get_user = await user_crud.get(tg_id=this_user.id)
        main_admin_id = int(os.getenv("ADMIN"))

        if get_user.tg_id == main_admin_id and (get_user is None or get_user.role != "ADMIN"):
            await user_crud.update(filters={"tg_id": this_user.id},
                                    updates={"role": "ADMIN"})

        return await handler(event, data)
