from typing import Any, Sequence, Callable, TypeVar, Optional
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.data.repositories.category_repository import category_crud
from src.data.repositories.product_repository import product_crud

T = TypeVar("T")


async def yes_no_kb(action:str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='✅ Да', callback_data=f'yes:{action}'),
        InlineKeyboardButton(text='❌ Нет', callback_data=f'no:{action}')
    )
    return builder.as_markup()

async def buy_item_kb(item_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для покупки товара.
    - item_id: ID товара для callback_data.
    """
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text='🛒 Купить', callback_data=f'buy:{item_id}'),
        InlineKeyboardButton(text='📦 В корзину', callback_data=f'add_to_cart:{item_id}'),
        InlineKeyboardButton(text='❌ Отмена', callback_data='cancel')
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

async def menu_builder_kb(
    items: Sequence[T],
    page: int = 0,
    *,
    prefix: str,
    text_func: Callable[[T], str],
    id_func: Callable[[T], Any],
    back_callback: Optional[str] = None,      # callback_data для кнопки «назад»
) -> InlineKeyboardMarkup:
    """
    Универсальный билдер меню с пагинацией.
    - items: список объектов для текущей страницы.
    - page: номер страницы (0-based).
    - prefix: префикс для callback_data, напр. "category" или "product".
    - text_func: как получить текст кнопки из элемента.
    - id_func: как получить id для callback_data из элемента.
    - back_callback: callback_data для кнопки «назад» (None — не показывать).
    - back_text: текст кнопки «назад».
    """
    builder = InlineKeyboardBuilder()

    # Кнопки для каждой сущности
    for item in items:
        text = text_func(item)
        _id  = id_func(item)
        cb   = f"{prefix}:{_id}:{page}"
        builder.row(InlineKeyboardButton(text=text, callback_data=cb))

    # Навигация по страницам
    prev_page = max(0, page - 1)
    next_page = page + 1
    builder.row(
        InlineKeyboardButton(
            text="⬅️ Предыдущая", 
            callback_data=f"{prefix}_page:{prev_page}"
        ),
        InlineKeyboardButton(
            text="Следующая ➡️", 
            callback_data=f"{prefix}_page:{next_page}"
        )
    )

    # Кнопка «Назад», если нужно
    if back_callback:
        builder.row(
            InlineKeyboardButton(text="🔙 Назад", callback_data=back_callback)
        )

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
