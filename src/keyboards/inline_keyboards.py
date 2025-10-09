from typing import Any, Sequence, Callable, TypeVar, Optional
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

T = TypeVar("T")

async def assessment_kb(tg_id: int, operation: str, *args) -> InlineKeyboardMarkup:
    """
    Клавиатура для оценки специалиста по шкале от 1 до 10.
    - tg_id: tg ID пользователя.
    - operation: тип оценки ("aoq" или "nps").
    - specialist_id: ID специалиста для callback_data.
    
    """

    builder = InlineKeyboardBuilder()
    if operation == "aoq":
        buttons = [
            InlineKeyboardButton(text=str(i), callback_data=f'aoq:{args[0]}:{i}')
            for i in range(1, 11)
        ]

    elif operation == "nps":
        buttons = [
            InlineKeyboardButton(text=str(i), callback_data=f'nps:{args[0]}:{i}')
            for i in range(0, 11)
        ]
        
    builder.row(*buttons)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
