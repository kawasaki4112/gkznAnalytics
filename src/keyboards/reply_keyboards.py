from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from src.data.repositories.user_repository import user_crud
from src.utils.const_functions import rkb

async def main_menu_kb(tg_id: int) -> ReplyKeyboardMarkup:
    _user = await user_crud.get(tg_id=tg_id)
    
    builder = ReplyKeyboardBuilder()
    
    if _user.role == "moderator":
        builder.row(
            rkb("🗂️ Соц. категории"),
            rkb("🛠️ Услуги"),
        )
        
        builder.row(
            rkb("👤 Специалисты"),
            rkb("📊 Аналитика"),
            rkb("💾 Выгрузить данные")
        )
        
        
    elif _user.role == "admin":
        builder.row(
            rkb("🗝️ Доступы"),
            rkb("💾 Выгрузить данные"),
        )
        
        builder.row(
            rkb("🗂️ Соц. категории"),
            rkb("🛠️ Услуги"),
        )
        
        builder.row(
            rkb("👤 Специалисты"),
            rkb("📊 Аналитика"),
            rkb("📢 Рассылка"),
        )
        
        builder.row(
            rkb("🗑 Сброс статистики")
        )
    
    else:
        return None
    
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
