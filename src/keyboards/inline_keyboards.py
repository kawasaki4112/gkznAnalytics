from typing import Any, Sequence, Callable, TypeVar, Optional
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

T = TypeVar("T")

async def assessment_kb(tg_id: int, *args) -> InlineKeyboardMarkup:
    """
    Клавиатура для оценки специалиста по шкале от 1 до 10.
    - tg_id: tg ID пользователя.
    - specialist_id: ID специалиста для callback_data.
    """

    builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text=str(i), callback_data=f'aoq:{args[0]}:{i}')
        for i in range(1, 11)
    ]
        
    builder.row(*buttons)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

async def accesses_kb():
    """
    Клавиатура для управления доступами.
    """
    builder = InlineKeyboardBuilder()
    buttons = [
        InlineKeyboardButton(text="Добавить администратора", callback_data='add_admin'),
        InlineKeyboardButton(text="Удалить администратора", callback_data='remove_admin'),
        InlineKeyboardButton(text="Добавить модератора", callback_data='add_moderator'),
        InlineKeyboardButton(text="Удалить модератора", callback_data='remove_moderator'),
    ]
        
    builder.row(*buttons)
    builder.row(InlineKeyboardButton(text="🏠 Главное меню", callback_data='main_menu'))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)