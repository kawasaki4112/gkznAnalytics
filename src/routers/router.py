from typing import Union
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

import src.keyboards.inline_keyboards as ikb
import src.keyboards.reply_keyboards as rkb


router = Router(name="user_router")

select_menu_item = "Выберите пункт меню:"

@router.callback_query(F.data.in_(['main_menu']))
@router.message(F.text.in_('🏠 Главное меню'))
@router.message(Command("start"))
async def start(event: Union[Message,CallbackQuery], state: FSMContext, command: CommandObject = None):
    await state.clear()
    
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(select_menu_item, reply_markup=rkb.main_menu_kb(event.from_user.id))
    
    elif isinstance(event, Message):
        if command.args:
            await event.answer("Оцените работу специалиста", 
                               reply_markup=await ikb.assessment_kb(
                                   event.from_user.id, "aoq", command.args))
        await event.answer("Привет! Я помощник ГКЗН по вопросам.")
