from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import src.keyboards.inline_keyboards as ikb
import src.keyboards.reply_keyboards as rkb


router = Router(name="admin_router")

select_menu_item = "Выберите пункт меню:"

# @router.message(F.text.in_(('🏠 Главное меню', '/start')))
# async def start(message: Message, state: FSMContext):
#     await message.answer(select_menu_item)