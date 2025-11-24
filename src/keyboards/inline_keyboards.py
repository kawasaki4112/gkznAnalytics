from typing import Any, Sequence, Callable, TypeVar, Optional
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.utils.const_functions import ikb

from src.data.repositories.socialCategory_repository import social_category_crud
from src.data.repositories.socialSubcategory_repository import social_subcategory_crud
from src.data.repositories.service_repository import service_crud


T = TypeVar("T")

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup



async def social_category_actions_kb() -> InlineKeyboardMarkup:
    """
    Клавиатура для управления социальными категориями и подкатегориями.
    """
    catergories = await social_category_crud.get_list()
    
    if len(catergories) > 0:
        buttons = (
            ikb(text="Импорт категорий JSON", callback_data='import_categories'),
            ikb(text="Добавить категорию", callback_data='add_category'),
            ikb(text="Удалить категорию", callback_data='remove_category'),
            ikb(text="Добавить подкатегорию", callback_data='add_subcategory@category'),
            ikb(text="Удалить подкатегорию", callback_data='remove_subcategory@category'),
        )
    else:
        buttons = (
            ikb(text="Импорт категорий JSON", callback_data='import_categories'),
            ikb(text="Добавить категорию", callback_data='add_category'),
            ikb(text="Удалить категорию", callback_data='remove_category'),
        )
    builder = InlineKeyboardBuilder()

        
    builder.row(*buttons)
    builder.adjust(1)
    builder.row(ikb(text="🏠 Главное меню", callback_data='main_menu'))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


async def social_category_selection_kb(
    _type: str, 
    action: str, 
    page: int = 1, 
    category_id: int = None
) -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора социальной категории или подкатегории с пагинацией.
    """
    per_page = 10
    if _type == "ctg":
        categories = await social_category_crud.get_list()
    else:
        categories = await social_subcategory_crud.get_list(category_id=category_id)

    total = len(categories)
    start = (page - 1) * per_page
    end = start + per_page
    sliced = categories[start:end]
    builder = InlineKeyboardBuilder()
    for category in sliced:
        builder.row(
            ikb(
                text=category.name, 
                callback_data=f'select@{_type}:{category.id}_{action}'
            )
        )

    # --- пагинация ---
    buttons = []
    if page > 1:
        buttons.append(
            ikb(
                text="⬅️", 
                callback_data=f'change_page@{_type}:{page-1}_{action}_{category_id or 0}'
            )
        )
    if end < total:
        buttons.append(
            ikb(
                text="➡️", 
                callback_data=f'change_page@{_type}:{page+1}_{action}_{category_id or 0}'
            )
        )
    if buttons:
        builder.row(*buttons)
    builder.row(ikb(text="🏠 Главное меню", callback_data='main_menu'))
    return builder.as_markup()


async def service_menu_kb() -> InlineKeyboardMarkup:
    """
    Клавиатура для выбора действия с услугами.
    """
    builder = InlineKeyboardBuilder()
    buttons = (
        ikb(text="Импорт услуг JSON", callback_data='menu@service:import'),
        ikb(text="Добавить услугу", callback_data='menu@service:add'),
        ikb(text="Удалить услугу", callback_data='menu@service:remove'),
        ikb(text="Просмотреть услуги", callback_data='menu@service:view'),
    )
        
    builder.row(*buttons)
    builder.row(ikb(text="🏠 Главное меню", callback_data='main_menu'))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

async def service_actions_kb(action: str, page: int = 1) -> InlineKeyboardMarkup:
    """
    Клавиатура для действий с услугами с пагинацией.
    """
    services = await service_crud.get_list()
    per_page = 10
    total = len(services)
    start = (page - 1) * per_page
    end = start + per_page

    builder = InlineKeyboardBuilder()
    
    # Кнопки для услуг на текущей странице
    for service in services[start:end]:
        builder.row(
            ikb(
                text=service.name, 
                callback_data=f'service_action:{action}_{service.id}'
            )
        )

    # --- пагинация ---
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            ikb(
                text="⬅️",
                callback_data=f'change_page@service:{action}_{page-1}'
            )
        )
    if end < total:
        pagination_buttons.append(
            ikb(
                text="➡️",
                callback_data=f'change_page@service:{action}_{page+1}'
            )
        )
    if pagination_buttons:
        builder.row(*pagination_buttons)

    # Главная кнопка
    builder.row(ikb(text="🏠 Главное меню", callback_data='main_menu'))

    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

async def assessment_score_kb(_type: str) -> InlineKeyboardMarkup:
    """
    Клавиатура для оценки качества.
    """
    builder = InlineKeyboardBuilder()
    
    buttons = (
        ikb(text="1", callback_data=f'assessment_score@{_type}:1'),
        ikb(text="2", callback_data=f'assessment_score@{_type}:2'),
        ikb(text="3", callback_data=f'assessment_score@{_type}:3'),
        ikb(text="4", callback_data=f'assessment_score@{_type}:4'),
        ikb(text="5", callback_data=f'assessment_score@{_type}:5'),
    )
    builder.row(*buttons)
    builder.row(ikb(text="🏠 Главное меню", callback_data='main_menu'))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)
    

    
async def accesses_kb():
    """
    Клавиатура для управления доступами.
    """
    builder = InlineKeyboardBuilder()
    buttons = (
        ikb(text="Добавить администратора", callback_data='add_admin'),
        ikb(text="Удалить администратора", callback_data='remove_admin'),
        ikb(text="Добавить модератора", callback_data='add_moderator'),
        ikb(text="Удалить модератора", callback_data='remove_moderator'),
    )
        
    builder.row(*buttons)
    builder.row(ikb(text="🏠 Главное меню", callback_data='main_menu'))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

async def specialist_action_kb():
    """
    Клавиатура для действий со специалистами.
    """
    builder = InlineKeyboardBuilder()
    buttons = (
        ikb(text="Импорт специалистов EXCEL", callback_data='import_specialists'),
        ikb(text="Просмотреть специалистов", callback_data='view_specialists'),
        ikb(text="Добавить специалиста", callback_data='add_specialist'),
        ikb(text="Удалить специалиста", callback_data='remove_specialist'),
    )

    builder.row(*buttons)
    builder.row(ikb(text="🏠 Главное меню", callback_data='main_menu'))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

async def spam_confirmation_kb():
    """
    Клавиатура для подтверждения рассылки.
    """
    builder = InlineKeyboardBuilder()
    buttons = (
        ikb(text="Подтвердить", callback_data='spam_confirmation:yes'),
        ikb(text="Отменить", callback_data='spam_confirmation:no'),
    )

    builder.row(*buttons)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)

async def reset_statistics_confirmation_kb():
    """
    Клавиатура для подтверждения сброса статистики.
    """
    builder = InlineKeyboardBuilder()
    buttons = (
        ikb(text="✅ Да, удалить все данные", callback_data='reset_statistics_confirm'),
        ikb(text="❌ Отмена", callback_data='reset_statistics_cancel'),
    )

    builder.row(*buttons)
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)