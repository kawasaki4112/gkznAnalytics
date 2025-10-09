from typing import Callable, Dict, Any, Union
from aiogram import BaseMiddleware
from aiogram.types import User, Message, CallbackQuery

from src.data.repositories.user_repository import user_crud


class ExistsUserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Any],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any],
    ) -> Any:
        this_user: User = data.get("event_from_user")

        if not this_user.is_bot:
            get_user = await user_crud.get(tg_id=this_user.id)

            user_id = this_user.id
            user_username = this_user.username or ""
            user_fullname = this_user.first_name+this_user.last_name if this_user.last_name else this_user.first_name or ""
            
            if get_user is None:
                await user_crud.create(tg_id=user_id, username=user_username.lower(), full_name=user_fullname)
            else:
                if get_user.username != user_username.lower():
                    await user_crud.update(
                        filters={"tg_id": get_user.tg_id},
                        updates={"username": user_username.lower(),
                                 "full_name": user_fullname}
                    )

        return await handler(event, data)
