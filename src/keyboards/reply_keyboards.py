from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.data.repositories.user_repository import user_crud


async def main_menu_kb(tg_id: int) -> ReplyKeyboardMarkup:
    _user = await user_crud.get(tg_id=tg_id)
    builder = ReplyKeyboardBuilder()
    if _user.role == "admin":
        builder.row(
            "🗝️ Доступы",
        )
    if _user.role in ["admin", "moderator"]:
        builder.row(
            "👤 Специалисты",
            "📊 Статистика",
            "💾 Выгрузить данные"
        )

    builder.adjust()
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

