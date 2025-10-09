from typing import Union
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from src.data.repositories.category_repository import category_crud
from src.data.repositories.product_repository import product_crud
import src.keyboards.inline_keyboards as ikb
import src.keyboards.reply_keyboards as rkb


router = Router(name="user_router")

select_menu_item = "Выберите пункт меню:"

@router.callback_query(F.data.in_(['main_menu']))
@router.message(F.text.in_(('🏠 Главное меню', '/start')))
async def start(event: Union[Message,CallbackQuery], state: FSMContext):
    await state.clear()
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(select_menu_item, reply_markup=rkb.main_menu_kb(event.from_user.id))
    else:
        await event.answer(select_menu_item, 
                             reply_markup=await rkb.main_menu_kb(event.from_user.id))
    
@router.message(F.text == "🛍️ Каталог")
async def catalog(message: Message, state: FSMContext):
    await state.clear()
    categories = await category_crud.get_categories()
    kb = await ikb.menu_builder_kb(
        items=categories,
        page=0,
        prefix="category",
        text_func=lambda c: c.name,
        id_func=lambda c: c.id,
        back_callback="main_menu",
    )
    await message.answer("Категории товаров:", reply_markup=kb)

@router.callback_query(F.data.startswith(['category_page:', 'product_page:']))
async def next_page(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split(':')[1])
    
    if 'category' in callback.data:
        items = await category_crud.get_categories(page=page)
        prefix = 'category'
        back_callback='main_menu'

    elif 'product' in callback.data:
        category_id = int(callback.data.split(':')[1])
        category_page = int(callback.data.split(':')[2])
        items = await product_crud.get_list(category_id=category_id)
        prefix = 'product'
        back_callback=f'category:{category_page}'
    
    kb = await ikb.menu_builder_kb(
        items=items,
        page=0,
        prefix=prefix,
        text_func=lambda c: c.name,
        id_func=lambda c: c.id,
        back_callback=back_callback,
    )
    await callback.message.edit_text(f"{prefix[0].capitalize()+prefix[0:]}:", reply_markup=kb)

@router.callback_query(F.data.startswith(['category:', 'product:']))
async def category(callback: CallbackQuery, state: FSMContext):
    item_id = int(callback.data.split(':')[1])
    last_items_page = int(callback.data.split(':')[2])
    if 'category' in callback.data:
        category_id = item_id
        products = await product_crud.get_list(category_id=category_id)
        kb = await ikb.menu_builder_kb(
            items=products,
            page=0,
            prefix='product',
            text_func=lambda p: p.name,
            id_func=lambda p: p.id,
            back_callback=f'category:{last_items_page}',
        )
        await callback.message.edit_text(f"Товары категории {category_id}:", reply_markup=kb)
    elif 'product' in callback.data:
        product_id = item_id
        product = await product_crud.get(product_id=product_id)
        if not product:
            await callback.answer("Товар не найден.", show_alert=True)
            return
        elif product.photo:
            await callback.message.delete()
            await callback.message.answer_photo(
                f"Товар: {product.name}\nОписание: {product.description}\nЦена: {product.price} руб.", photo=product.photo,
                reply_markup=ikb.yes_no_keyboard(action='view_products')
            )
        else:
            await callback.message.edit_text(
                f"Товар: {product.name}\nОписание: {product.description}\nЦена: {product.price} руб.",
                reply_markup=ikb.yes_no_keyboard(action='view_products')
            )
        return
    
    await callback.message.edit_text(f"Товары категории {category_id}:", reply_markup=ikb.yes_no_keyboard(action='view_products'))
