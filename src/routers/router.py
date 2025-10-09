from typing import Union
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

import src.keyboards.inline_keyboards as ikb
import src.keyboards.reply_keyboards as rkb
from src.data.models import UserRole
from src.data.repositories.user_repository import user_crud

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
        else:
            user = await user_crud.get_by_tg_id(event.from_user.id)
            await event.answer(f"Привет! Я помощник ГКЗН по вопросам. {user.full_name}, {user.created_at}, {user.modified_at}",)

@router.message(F.text.in_('🗝️ Доступы'))
async def manage_access(event: Message, state: FSMContext):
    await state.clear()
    
    await event.answer(select_menu_item, reply_markup=await ikb.accesses_kb())
    
@router.callback_query(F.data.in_(['add_admin', 'remove_admin', 'add_moderator', 'remove_moderator']))
async def manage_access_callback(event: CallbackQuery, state: FSMContext):
    await state.clear()

    await event.message.edit_text(f"Введите username для {"добавления" if event.data.startswith('add') else "удаления"}:", reply_markup=None)
    await state.set_state(event.data)
    
@router.message(F.text)
async def handle_username(event: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state in ['add_admin', 'remove_admin', 'add_moderator', 'remove_moderator']:
        username = event.text.strip().lstrip('@')
        action = "added" if current_state.startswith("add") else "removed"
        role = "admin" if "admin" in current_state else "moderator"
        
        if action == "removed":
            await rkb.user_crud.update(
                filters={"username": username},
                updates={"role": UserRole.USER.value}
            )
        else:
            await rkb.user_crud.update(
                filters={"username": username},
                updates={"role": role}
            )
        
        
        await event.answer(f"User @{username} has been {action} as {role}.", reply_markup=await rkb.main_menu_kb(event.from_user.id))
        await state.clear()