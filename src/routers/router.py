import os, asyncio, json
import pandas as pd
from typing import Union
from uuid import UUID
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

import src.keyboards.inline_keyboards as ikb
import src.keyboards.reply_keyboards as rkb
import src.states as st
from src.data.models import UserRole, tz_now_naive
from src.data.repositories.user_repository import user_crud
from src.data.repositories.specialist_repository import specialist_crud
from src.data.repositories.service_repository import service_crud
from src.data.repositories.assessmentOfQuality_repository import aoq_crud
from src.data.repositories.netPromoterScore_repository import nps_crud
from src.data.repositories.socialCategory_repository import social_category_crud
from src.data.repositories.socialSubcategory_repository import social_subcategory_crud
from src.utils.misc_functions import spam_message, backup_db, send_backup_file, send_analytics, send_full_statistics_excel

router = Router(name="user_router")

select_menu_item = "Выберите пункт меню:"

@router.callback_query(F.data.in_(['main_menu']))
@router.message(F.text.in_('🏠 Главное меню'))
@router.message(Command("start"))
async def start(event: Union[Message,CallbackQuery], state: FSMContext, command: CommandObject = None):
    await state.clear()
    user = await user_crud.get(tg_id=event.from_user.id)
    if isinstance(event, CallbackQuery):
        await event.message.delete()
        await event.message.answer(select_menu_item, reply_markup=await rkb.main_menu_kb(user.tg_id))
    
    elif isinstance(event, Message):
        if command.args:
            aoq_list = await aoq_crud.get_list(user_id=user.id)
            now = tz_now_naive()
            last_week = now - timedelta(days=7)
            
            aoq_on_last_7_days = False
            for aoq in aoq_list:
                if aoq.created_at > last_week:
                    aoq_on_last_7_days = True
                    break

            # если была оценка за последние 7 дней → запрещаем
            if aoq_on_last_7_days:
                await event.answer(
                    "Вы уже оставляли оценку за последние 7 дней. Спасибо!",
                    reply_markup=await rkb.main_menu_kb(user.tg_id)
                )
            else:
                await event.answer(
                    "Пожалуйста, выберите вашу социальную категорию:",
                    reply_markup=await ikb.social_category_selection_kb(_type="ctg", action="select")
                )
                await state.set_state(st.UserStates.waiting_for_social_category)
                await state.update_data(specialist_id=command.args)

        else:
            await event.answer(f"Привет! Я помощник ГКЗН", reply_markup=await rkb.main_menu_kb(user.tg_id))

@router.message(Command("cancel_input"))
async def cancel_input(event: Message, state: FSMContext):
    await state.clear()
    await event.answer("Ввод отменен", reply_markup=await rkb.main_menu_kb(event.from_user.id))

#####################################################################################################################################
############################################################## Доступы ##############################################################
#####################################################################################################################################

@router.message(F.text.in_('🗝️ Доступы'))
async def manage_access(event: Message, state: FSMContext):
    await state.clear()
    
    await event.answer(select_menu_item, reply_markup=await ikb.accesses_kb())
    
@router.callback_query(F.data.in_(['add_admin', 'remove_admin', 'add_moderator', 'remove_moderator']))
async def manage_access_callback(event: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.update_data(action=event.data)
    await event.message.edit_text(f"Введите username для {"добавления" if event.data.startswith(('add')) else "удаления"}:", reply_markup=None)
    await state.set_state(st.UserStates.waiting_for_username)

@router.message(st.UserStates.waiting_for_username)
async def process_username(event: Message, state: FSMContext):
    await state.update_data(username=event.text)
    data = await state.get_data()
    await state.clear()
    if data['action'] in ['add_admin', 'remove_admin', 'add_moderator', 'remove_moderator']:
        username = event.text.strip().lstrip('@')
        action = "added" if data['action'].startswith(("add")) else "removed"
        role = "admin" if "admin" in data['action'] else "moderator"

        if action == "removed":
            await user_crud.update(
                filters={"username": username},
                updates={"role": UserRole.USER.value}
            )
        else:
            await user_crud.update(
                filters={"username": username},
                updates={"role": role}
            )


        await event.answer(f"Пользователь @{username} был {"удален" if action == "removed" else "добавлен"} как {"администратор" if role == "admin" else "модератор"}.", reply_markup=await rkb.main_menu_kb(event.from_user.id))
        await state.clear()
        
#########################################################################################################################################
############################################################## Специалисты ##############################################################
#########################################################################################################################################

@router.message(F.text.in_('👤 Специалисты'))
async def manage_specialists(event: Message, state: FSMContext):
    await state.clear()

    await event.answer(select_menu_item, reply_markup=await ikb.specialist_action_kb())

@router.callback_query(F.data.in_(['import_specialists', 'view_specialists', 'add_specialist', 'remove_specialist']))
async def manage_specialists_callback(event: CallbackQuery, state: FSMContext):
    await state.clear()
    
    if event.data == 'import_specialists':
        await event.message.edit_text("Отправьте файл с данными специалистов в формате EXCEL.", reply_markup=None)
        await state.set_state(st.SpecialistStates.waiting_for_specialist_import)
    
    elif event.data == 'view_specialists':
        await event.message.delete()
        specialists = await specialist_crud.get_list()
        if not specialists:
            await event.message.answer("Список специалистов пуст.", reply_markup=await ikb.specialist_action_kb())
            return

        lines = [
            f"{idx+1}. {spec.fullname} — {spec.position} в {spec.organization}\n🔗 {spec.link or 'ссылка отсутствует'}"
            for idx, spec in enumerate(specialists)
        ]

        chunks = []
        current = ""
        for line in lines:
            if len(current) + len(line) + 1 > 4000:
                chunks.append(current)
                current = ""
            current += line + "\n"
        if current:
            chunks.append(current)

        await event.message.answer("*Список специалистов:*", parse_mode="HTML")
        for chunk in chunks:
            await event.message.answer(f"\n{chunk}", parse_mode="HTML")

        await event.message.answer(select_menu_item, reply_markup=await ikb.specialist_action_kb())


    elif event.data == 'add_specialist':
        await event.message.edit_text("Напишите ФИО специалиста:", reply_markup=None)
        await state.set_state(st.SpecialistStates.waiting_for_specialist_fio)

    elif event.data == 'remove_specialist':
        await event.message.edit_text("Напишите ФИО специалиста для удаления:", reply_markup=None)
        await state.set_state(st.SpecialistStates.waiting_for_specialist_fio)
        
        await state.update_data(action='remove_specialist')

@router.message(st.SpecialistStates.waiting_for_specialist_import)
async def process_specialist_import(event: Message, state: FSMContext):
    # === 1. Проверка файла ===
    if not event.document:
        await event.answer("📄 Пожалуйста, отправьте файл в формате Excel (.xls или .xlsx).")
        return

    if not event.document.file_name.lower().endswith(('.xls', '.xlsx')):
        await event.answer("⚠️ Неверный формат файла. Загрузите Excel (.xls, .xlsx).")
        return

    # === 2. Скачиваем файл ===
    os.makedirs("src/files", exist_ok=True)
    file_info = await event.bot.get_file(event.document.file_id)
    file_path = f"src/files/{event.document.file_name}"
    await event.bot.download_file(file_info.file_path, destination=file_path)

    # === 3. Читаем Excel ===
    df = pd.read_excel(file_path, sheet_name="Сотрудники").where(pd.notnull, None)

    # === 4. Кэшируем username бота ===
    bot_username = (await event.bot.get_me()).username

    created_count = 0
    specialists_to_create = []

    for _, row in df.iterrows():
        row_data = {
            "organization": row["Организация"],
            "position": row["Должность"],
            "fullname": row["ФИО"],
            "department": row["Отдел"],
        }

        existing = await specialist_crud.get(**row_data)
        if not existing:
            specialists_to_create.append(row_data)

    for spec in specialists_to_create:
        spec_obj = await specialist_crud.create(**spec)
        await specialist_crud.update(
            filters={
                "organization": spec["organization"],
                "position": spec["position"],
                "fullname": spec["fullname"]
            },
            updates={"link": f"https://t.me/{bot_username}?start={spec_obj.id}"}
        )
        created_count += 1

    try:
        os.remove(file_path)
    except FileNotFoundError:
        pass

    await event.answer(
        f"Файл обработан.\nДобавлено {created_count} новых специалистов.",
        reply_markup=await ikb.specialist_action_kb()
    )
    await state.clear()

@router.message(st.SpecialistStates.waiting_for_specialist_fio)
async def process_specialist_fio(event: Message, state: FSMContext):
    await state.update_data(fullname=event.text)
    data = await state.get_data()
    
    current_state = await state.get_state()
    
    if current_state == st.SpecialistStates.waiting_for_specialist_fio:
        if 'remove_specialist' in (await state.get_data()).get('action', ''):
            await specialist_crud.delete(fullname=data['fullname'])
            await event.answer(f"Специалист {data['fullname']} был удален.", reply_markup=await rkb.main_menu_kb(event.from_user.id))
            await state.clear()
        else:
            await event.answer("Напишите организацию, в которой работает специалист:")
            await state.set_state(st.SpecialistStates.waiting_for_specialist_organization)
    
@router.message(st.SpecialistStates.waiting_for_specialist_organization)
async def process_specialist_organization(event: Message, state: FSMContext):
    await state.update_data(organization=event.text)
    await event.answer("Напишите отдел, в котором работает специалист (если есть, если нет отправьте знак минуса):")
    await state.set_state(st.SpecialistStates.waiting_for_specialist_department)

@router.message(st.SpecialistStates.waiting_for_specialist_department)
async def process_specialist_department(event: Message, state: FSMContext):
    await state.update_data(department=event.text)
    await event.answer("Напишите должность специалиста:")
    await state.set_state(st.SpecialistStates.waiting_for_specialist_position)
    
@router.message(st.SpecialistStates.waiting_for_specialist_position)
async def process_specialist_position(event: Message, state: FSMContext):
    await state.update_data(position=event.text)
    data = await state.get_data()
    bot = await event.bot.get_me()
    specialist = await specialist_crud.create(
            organization=data['organization'],
            position=data['position'],
            fullname=data['fullname'],
            department=data.get('department'),
        )
        
    await specialist_crud.update(
            filters={"fullname": data['fullname'], "organization": data['organization']},
            updates={"link": f"https://t.me/{bot.username}?start={specialist.id}"}
        )
        
    await event.answer(f"Специалист {data['fullname']} был добавлен.", reply_markup=await rkb.main_menu_kb(event.from_user.id))
    await state.clear()
    
#############################################################################################################################################
############################################################## Оценка качества ##############################################################
#############################################################################################################################################

@router.callback_query(F.data.startswith(('change_page@service:')))
async def change_service_page(event: CallbackQuery, state: FSMContext):
    data_parts = event.data.split(':')
    parts = data_parts[1].split('_')

    action = parts[0]
    page = parts[1]
        
    await event.message.edit_text("Выберите услугу для оценки:", 
                                 reply_markup=await ikb.service_actions_kb(action=action, page=int(page)))

@router.callback_query(F.data.startswith(('service_action:')))
async def process_assessment_service(event: CallbackQuery, state: FSMContext):
    data_parts = event.data.split(':')
    action = data_parts[-1].split('_')[0]
    service_id = data_parts[-1].split('_')[-1]
    if action == "select":
        await state.update_data(assessment_service_id=service_id)
        await event.message.edit_text("Оцените качество обслуживания по шкале от 1 до 5:", reply_markup=await ikb.assessment_score_kb(_type = "aoq"))
        await state.set_state(st.UserStates.waiting_for_assessment_score)
    elif action == "remove":
        await service_crud.delete(id=str(service_id))
        await event.message.edit_text("Услуга была удалена.", reply_markup=await ikb.service_menu_kb())
    elif action == "view":
        return

@router.callback_query(F.data.startswith(('assessment_score@')), StateFilter(st.UserStates.waiting_for_assessment_score))
async def process_assessment_score(event: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    data_parts = event.data.split('@') # ['assessment_score', 'aoq:5']
    _type = data_parts[-1].split(':')[0]
    score = int(data_parts[-1].split(':')[-1])
    user = await user_crud.get(tg_id=event.from_user.id)
    
    if _type == "aoq":
        aoq = await aoq_crud.create(
            user_id=user.id,
            specialist_id=state_data.get('specialist_id'),
            service_id=state_data.get('assessment_service_id'),
            score=score,
        )
        await event.message.edit_text("Напишите предложения по улучшению", reply_markup=None)
        await state.update_data(aoq_id=aoq.id)
        await state.set_state(st.UserStates.waiting_for_assessment_comment)
        asyncio.create_task(send_nps(event, state, aoq.id))
    else:
        aoq_id = state_data.get('aoq_id')
        await nps_crud.create(
            user_id=str(user.id),
            aoq_id=str(aoq_id),
            score=score,
        )

        await event.message.edit_text("Спасибо за вашу оценку!", reply_markup=None)

@router.message(st.UserStates.waiting_for_assessment_comment)
async def process_assessment_comment(event: Message, state: FSMContext):
    data = await state.get_data()
    aoq_id = data.get('aoq_id')
    if aoq_id:
        await aoq_crud.update(
            filters={"id": aoq_id},
            updates={"comment": event.text}
        )
        await event.answer("Спасибо за ваши предложения по улучшению!", reply_markup=await rkb.main_menu_kb(event.from_user.id))
    await state.clear()


async def send_nps(event: Message, state: FSMContext, aoq_id: str):
    nps_delay = int(os.getenv("NPS_DELAY_MINUTES", "10")) * 60
    await asyncio.sleep(nps_delay)
    await event.message.answer("Пожалуйста, оцените вашу общую удовлетворенность услугой, порекомендуете ли вы нас?", 
                       reply_markup=await ikb.assessment_score_kb(_type="nps"))
    await state.set_state(st.UserStates.waiting_for_assessment_score)
    await state.update_data(aoq_id=aoq_id)
    
######################################################################################################################################
############################################################## Рассылка ##############################################################
######################################################################################################################################

@router.message(F.text.in_('📢 Рассылка'))
async def process_spam_message(event: Message, state: FSMContext):
    await state.clear()
    await state.set_state(st.SpamStates.waiting_for_spam_text)
    await event.answer("📢 Отправьте пост для рассылки пользователям\n"
                       "❕ Поддерживаются посты с любыми медиафайлами",
                       )
    
@router.message(st.SpamStates.waiting_for_spam_text)
async def process_spam_text(event: Message, state: FSMContext):
    await state.update_data(spam_message=event)
    
    users = await user_crud.get_list()

    await event.answer(f"Вы уверены, что хотите отправить это сообщение {len(users)} пользователям?", reply_markup=await ikb.spam_confirmation_kb())

@router.callback_query(F.data.startswith(('spam_confirmation')))
async def process_spam_confirmation(event: CallbackQuery, state: FSMContext):
    status = event.data.split(':')[-1]
    data = await state.get_data()
    send_message = data.get('spam_message')
    await state.clear()
    
    if status == 'yes':
        users = await user_crud.get_list()

        await event.message.edit_text(f"Рассылка началась... (0/{len(users)})", reply_markup=None)

        await asyncio.create_task(spam_message(event, send_message))

    else:
        await event.answer("Рассылка отменена.", reply_markup=await rkb.main_menu_kb(event.from_user.id))


############################################################################################################################################
############################################################## Соц. категории ##############################################################
############################################################################################################################################

@router.message(F.text.in_('🗂️ Соц. категории'))
async def manage_social_categories(event: Message, state: FSMContext):
    await state.clear()
    await event.answer(select_menu_item, reply_markup=await ikb.social_category_actions_kb())

@router.callback_query(F.data.in_(['import_categories', 'add_category', 'remove_category', 'add_subcategory@category', 'remove_subcategory@category', 'add_subcategory', 'remove_subcategory']))
async def manage_social_categories_callback(event: CallbackQuery, state: FSMContext):
    await state.clear()

    if event.data == 'import_categories':
        await event.message.edit_text("Отправьте файл с категориями в формате JSON:", reply_markup=None)
        await state.set_state(st.CategoryStates.waiting_for_category_import)

    #done
    elif event.data == 'add_category':
        await event.message.edit_text("Напишите название новой социальной категории:", reply_markup=None)
        await state.set_state(st.CategoryStates.waiting_for_category_name)
    
    #done
    elif event.data == 'remove_category':
        await event.message.edit_text("Выберите категорию для удаления:", reply_markup=await ikb.social_category_selection_kb(_type="ctg", action="delete"))

    #done
    elif event.data == 'add_subcategory@category':
        await event.message.edit_text("Выберите категорию, к которой хотите добавить подкатегорию:",
                                      reply_markup=await ikb.social_category_selection_kb(_type="ctg", action="addsubcategory"))

    #done
    elif event.data == 'remove_subcategory@category':
        await event.message.edit_text("Выберите категорию, из которой хотите удалить подкатегорию:",
                                      reply_markup=await ikb.social_category_selection_kb(_type="ctg", action="removesubcategory"))

@router.message(st.CategoryStates.waiting_for_category_import)
async def process_category_import(event: Message, state: FSMContext):
    # === 1. Проверка файла ===
    if not event.document:
        await event.answer("📄 Пожалуйста, отправьте файл в формате JSON.")
        return

    if not event.document.file_name.lower().endswith('.json'):
        await event.answer("⚠️ Неверный формат файла. Загрузите JSON файл.")
        return

    # === 2. Скачиваем файл ===
    os.makedirs("src/files", exist_ok=True)
    file_info = await event.bot.get_file(event.document.file_id)
    file_path = f"src/files/{event.document.file_name}"
    await event.bot.download_file(file_info.file_path, destination=file_path)

    # === 3. Читаем JSON ===
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except ValueError:
        await event.answer("⚠️ Ошибка при чтении JSON файла. Пожалуйста, убедитесь, что файл корректен.")
        return

    # === 4. Удаляем старые записи ===
    await social_subcategory_crud.delete_all()
    await social_category_crud.delete_all()
    
    # === 5. Импортируем в БД ===
    created_count = 0
    for category in data:
        # Создаём категорию
        new_category = await social_category_crud.create(
            name=category["name"]
        )
        created_count += 1

        # Создаём подкатегории
        for sub in category.get("subcategories", []):
            await social_subcategory_crud.create(
                name=sub["name"],
                category_id=new_category.id
            )
            created_count += 1
    os.remove(file_path)
    await event.answer(f"✅ Импорт завершён! Создано {created_count} записей.", reply_markup=await ikb.social_category_actions_kb())
    await state.clear()
    
@router.message(st.CategoryStates.waiting_for_category_name)
async def process_category_name(event: Message, state: FSMContext):
    await state.update_data(category_name=event.text)
    
    await social_category_crud.create(name=event.text)
    await event.answer(f'Категория "{event.text}" была добавлена.', reply_markup=await ikb.social_category_actions_kb())
    await state.clear()

@router.callback_query(F.data.startswith(('change_page@ctg:', 'change_page@subctg:')))
async def categories_process(event: CallbackQuery, state: FSMContext):
    data_parts = event.data.split(':')
    _type = data_parts[0].split('@')[-1]
    
    parts = data_parts[1].split('_')
    
    page = parts[0]
    action = parts[1]
    category_id = parts[2] if len(parts) > 2 else None
    if _type == "ctg":
       await event.message.edit_text("Выберите категорию:", 
                                        reply_markup=await ikb.social_category_selection_kb(_type=_type, action=action, page=int(page)))
    else:
       await event.message.edit_text("Выберите подкатегорию:", 
                                        reply_markup=await ikb.social_category_selection_kb(_type=_type, action=action, page=int(page), category_id=category_id))

@router.callback_query(F.data.startswith(('select@')))
async def select_category_process(event: CallbackQuery, state: FSMContext):    
    data_parts = event.data.split('@', 1)
    parts = data_parts[-1].split(':')
    _type = parts[0]
    parts = parts[1].split('_') 
    id = parts[0] 
    action = parts[1]
    
    if _type == "ctg":
        if action == "delete":
            await social_category_crud.delete(id=str(id))
            await event.message.edit_text("Категория была удалена.", reply_markup=await ikb.social_category_actions_kb())
        
        elif action == "addsubcategory":
            await event.message.edit_text("Напишите название новой подкатегории:", reply_markup=None)
            await state.update_data(category_id=str(id))
            await state.set_state(st.SubCategoryStates.waiting_for_subcategory_name)
        
        elif action == "removesubcategory":
            await event.message.edit_text("Выберите подкатегорию для удаления:", 
                                          reply_markup=await ikb.social_category_selection_kb(_type="subctg", action="delete", category_id=str(id)))
        
        elif action == "select":
            await event.message.edit_text("Выберите подкатегорию:", 
                                          reply_markup=await ikb.social_category_selection_kb(_type="subctg", action="select", category_id=str(id)))

    else:
        if action == "delete":
            await social_subcategory_crud.delete(id=str(id))
            await event.message.edit_text("Подкатегория была удалена.", reply_markup=await ikb.social_category_actions_kb())
        elif action == "select":
            data = await state.get_data()
            specialist_id = data.get('specialist_id')
            if specialist_id:
                await user_crud.update(
                    filters={"tg_id": event.from_user.id},
                    updates={"social_subcategory_id": str(id)}
                )
                await event.message.edit_text("Спасибо! Ваша социальная категория была сохранена.\nВыберите услугу для оценки:", reply_markup=await ikb.service_actions_kb(action = "select"))
                await state.set_state(st.UserStates.waiting_for_assessment_service)

@router.message(st.SubCategoryStates.waiting_for_subcategory_name)
async def process_subcategory_name(event: Message, state: FSMContext):
    data = await state.get_data()
    category_id = data.get('category_id')
    subctg = await social_subcategory_crud.get(name=event.text)
    if category_id:
        if subctg:
            await event.answer(f'Подкатегория "{event.text}" уже существует. Пожалуйста, введите другое название.')
            await state.set_state(st.SubCategoryStates.waiting_for_subcategory_name)
            return
        await social_subcategory_crud.create(name=event.text, category_id=category_id)
        await event.answer(f'Подкатегория "{event.text}" была добавлена.', reply_markup=await ikb.social_category_actions_kb())
    await state.clear()
    
    
####################################################################################################################################
############################################################## Услуги ##############################################################
####################################################################################################################################

@router.message(F.text.in_('🛠️ Услуги'))
async def process_services(event: Message, state: FSMContext):
    await event.answer(select_menu_item, reply_markup=await ikb.service_menu_kb())

@router.callback_query(F.data.startswith(('menu@service:')))
async def service_menu_handler(event: CallbackQuery, state: FSMContext):
    action = event.data.split(':')[1]
    if action == "import":
        await event.message.edit_text("Отправьте файл с услугами в формате JSON:", reply_markup=None)
        await state.set_state(st.ServiceStates.waiting_for_service_import)
    elif action == "add":
        await event.message.edit_text("Напишите название новой услуги:", reply_markup=None)
        await state.set_state(st.ServiceStates.waiting_for_service_name)
    elif action == "remove":
        await event.message.edit_text("Выберите услугу для удаления:\n\n Внимание! При удалении услуги во всех связанных с ней оценках будут удалены поля услуг!\nт.е. нельзя будет узнать к какой услуге принадлежит оценка.",
                                      reply_markup=await ikb.service_actions_kb(action="remove"))
    elif action == "view":
        await event.message.edit_text("Посмотореть услуги", reply_markup=await ikb.service_actions_kb(action="view"))
        
@router.message(st.ServiceStates.waiting_for_service_name)
async def process_service_name(event: Message, state: FSMContext):
    service = await service_crud.create(name=event.text)

    await event.answer(f'Услуга "{service.name}" была добавлена.', reply_markup=await ikb.service_menu_kb())
    await state.clear()
    
@router.message(st.ServiceStates.waiting_for_service_import)
async def process_service_import(event: Message, state: FSMContext):
    # === 1. Проверка файла ===
    if not event.document:
        await event.answer("📄 Пожалуйста, отправьте файл в формате JSON.")
        return

    if not event.document.file_name.lower().endswith('.json'):
        await event.answer("⚠️ Неверный формат файла. Загрузите JSON файл.")
        return

    # === 2. Скачиваем файл ===
    os.makedirs("src/files", exist_ok=True)
    file_info = await event.bot.get_file(event.document.file_id)
    file_path = f"src/files/{event.document.file_name}"
    await event.bot.download_file(file_info.file_path, destination=file_path)

    # === 3. Читаем JSON ===
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except ValueError:
        await event.answer("⚠️ Ошибка при чтении JSON файла. Пожалуйста, убедитесь, что файл корректен.")
        return
    # === 4. Удаляем старые записи ===
    await service_crud.delete_all()

    # === 5. Импортируем в БД ===
    created_count = 0
    for service in data:
        await service_crud.create(
            name=service["name"]
        )
        created_count += 1
    os.remove(file_path)
    await event.answer(f"✅ Импорт завершён! Создано {created_count} записей.")
    await state.clear()

#######################################################################################################################################
############################################################## backup_db ##############################################################
#######################################################################################################################################

@router.message(F.text.in_('💾 Выгрузить данные'))
async def process_backup_db(event: Message, state: FSMContext):
    await state.clear()
    
    await event.answer("Выгрузка данных начата...")
    await backup_db(bot=event.bot)
    await send_backup_file(bot=event.bot)
    
#######################################################################################################################################
############################################################## Аналитика ##############################################################
#######################################################################################################################################

@router.message(F.text.in_('📊 Аналитика'))
async def process_analytics(event: Message, state: FSMContext):
    await state.clear()
    
    await send_analytics(bot=event.bot, user_tg_id=event.from_user.id)
    await send_full_statistics_excel(bot=event.bot, user_tg_id=event.from_user.id)