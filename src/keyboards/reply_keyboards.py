from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.data.repositories.user_repository import user_crud


async def main_menu_kb(tg_id: int) -> ReplyKeyboardMarkup:
    user_ = await user_crud.get(tg_id=tg_id)
    builder = ReplyKeyboardBuilder()
    builder.row(
        "🛍️ Каталог",
        "📦 Заказы"
        "🛒 Корзина"
    )
    builder.row(
        "👤 Профиль",
        "🆘 Помощь и поддержка"
    )
    if user_.role == "admin":
        builder.row(
            "👨‍💼 Админка",
            "📊 Статистика",
            "⚙️ Настройки",
        )
    builder.adjust()
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

