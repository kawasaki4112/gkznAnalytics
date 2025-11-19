import os
import asyncio
import aiofiles.os
import subprocess
import json
import tempfile
import pandas as pd
from datetime import datetime, timedelta
from typing import Union
from urllib.parse import urlparse
from openpyxl import Workbook

from aiogram import Bot
from aiogram.types import FSInputFile, CallbackQuery, Message

from src.data.repositories.user_repository import user_crud
from src.data.repositories.specialist_repository import specialist_crud
from src.data.repositories.service_repository import service_crud
from src.data.repositories.assessmentOfQuality_repository import aoq_crud
from src.data.repositories.netPromoterScore_repository import nps_crud
from src.data.db import db_url
from src.data.models import tz_now_naive
# # Автоматическая очистка ежедневной статистики после 00:00:15
# async def update_profit_day(bot: Bot):
#     await send_admins(bot, get_statistics())

#     Settingsx.update(misc_profit_day=get_unix())


# # Автоматическая очистка еженедельной статистики в понедельник 00:00:10
# async def update_profit_week():
#     Settingsx.update(misc_profit_week=get_unix())


# # Автоматическое обновление счётчика каждый месяц первого числа в 00:00:05
# async def update_profit_month():
#     Settingsx.update(misc_profit_month=get_unix())

async def cleanup_old_backups(folder_path="src/data/backups", keep_latest=7):
    await asyncio.to_thread(os.makedirs, folder_path, exist_ok=True)
    
    # Получаем список файлов
    dump_files = [
        f for f in await aiofiles.os.listdir(folder_path)
        if f.startswith("backup_") and f.endswith(".dump")
    ]
    
    if len(dump_files) <= keep_latest:
        return  # Нет лишних файлов
    
    # Полные пути
    full_paths = [os.path.join(folder_path, f) for f in dump_files]
    
    # Получаем время модификации асинхронно
    async def get_mtime(path):
        stat = await aiofiles.os.stat(path)
        return stat.st_mtime

    mtimes = await asyncio.gather(*(get_mtime(p) for p in full_paths))
    
    # Сортируем файлы по времени изменения (от старого к новому)
    sorted_files = [p for _, p in sorted(zip(mtimes, full_paths))]
    
    # Удаляем старые, оставляя keep_latest последних
    files_to_delete = sorted_files[:-keep_latest]
    
    for file_path in files_to_delete:
        try:
            await aiofiles.os.remove(file_path)
            print(f"Удалён старый бэкап: {file_path}")
        except Exception as e:
            print(f"Ошибка при удалении {file_path}: {e}")

async def backup_db(bot: Bot):
    admins = await user_crud.get_list(role="admin")
    now = tz_now_naive().date()
    filepath = f"src/data/backups/backup_{now}.dump"

    parsed = urlparse(db_url)
    DB_USER = parsed.username
    DB_PASSWORD = parsed.password
    DB_HOST = parsed.hostname
    DB_PORT = parsed.port or 5432
    DB_NAME = parsed.path.lstrip("/")
    
    proc = await asyncio.create_subprocess_exec(
    "pg_dump",
    "-h", DB_HOST,
    "-p", str(DB_PORT),
    "-U", DB_USER,
    "-F", "c",
    "-f", filepath,
    DB_NAME,
    env={**os.environ, "PGPASSWORD": DB_PASSWORD},
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
)
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        print(f"❌ Ошибка при создании бэкапа: {stderr.decode()}")
        for admin in admins:
            try:
                await bot.send_message(
                    chat_id=admin.tg_id,
                    text=f"❌ Ошибка при создании бэкапа базы данных:\n<code>{stderr.decode()}</code>"
                )
            except Exception as e:
                print(f"❌ Ошибка при отправке сообщения администратору {admin.tg_id}: {e}")
                
    await cleanup_old_backups()

async def send_backup_file(bot: Bot):
    admins = await user_crud.get_list(role="admin")
    path = "src/data/backups"

    dump_files = [
        f for f in await aiofiles.os.listdir(path)
        if f.startswith("backup_") and f.endswith(".dump")
    ]

    if not dump_files:
        return None

    full_paths = [os.path.join(path, f) for f in dump_files]

    async def get_mtime(path):
        stat = await aiofiles.os.stat(path)
        return stat.st_mtime

    mtimes = await asyncio.gather(*(get_mtime(p) for p in full_paths))
    latest_file = max(zip(full_paths, mtimes), key=lambda x: x[1])[0]

    backup_file = FSInputFile(latest_file)

    for admin in admins:
        try:
            await bot.send_document(
                chat_id=admin.tg_id,
                document=backup_file,
                caption="✅ Выгрузка данных завершена."
            )
        except Exception as e:
            print(f"❌ Ошибка при отправке бэкапа администратору {admin.tg_id}: {e}")

async def spam_message(event: CallbackQuery, message: Message):
    users_receive, users_block, users_count = 0, 0, 0

    users = await user_crud.get_list()

    for user in users:
        try:
            await event.bot.copy_message(
                chat_id=user.tg_id,
                from_chat_id=message.from_user.id,
                message_id=message.message_id,
            )
            users_receive += 1
        except Exception as ex:
            users_block += 1

        users_count += 1

        if users_count % 10 == 0:
            await event.message.edit_text(f"<b>📢 Рассылка началась... ({users_count}/{len(users)})</b>")

        await asyncio.sleep(0.07)

    await event.message.edit_text(
            "📢 Рассылка была завершена"+
            "\n➖➖➖➖➖➖➖➖➖➖"+
            f"\n👤 Всего пользователей: {len(users)}"+
            f"\n✅ Доставлено: {users_receive}"+
            f"\n❌ Не доставлено: {users_block}"
    )

async def send_analytics(bot: Bot, user_tg_id: int):
    now = tz_now_naive()
    last_month = now - timedelta(days=30)
    last_week = now - timedelta(days=7)

    specialists = await specialist_crud.get_list()
    services = await service_crud.get_list()
    all_aoqs = await aoq_crud.get_list()
    all_nps = await nps_crud.get_list()

    # --- АНАЛИТИКА ЗА МЕСЯЦ ---
    avg_score_by_specialist_month = {}
    avg_score_by_service_month = {}

    for spec in specialists:
        scores = [aoq.score for aoq in all_aoqs if aoq.specialist_id == spec.id and aoq.created_at >= last_month]
        if scores:
            avg_score_by_specialist_month[spec.fullname] = float(sum(scores)/len(scores))

    for service in services:
        scores = [aoq.score for aoq in all_aoqs if aoq.service_id == service.id and aoq.created_at >= last_month]
        if scores:
            avg_score_by_service_month[service.name] = float(sum(scores)/len(scores))

    total_aoq_month = len([aoq for aoq in all_aoqs if aoq.created_at >= last_month])
    total_nps_month = len([nps for nps in all_nps if nps.created_at >= last_month])

    top_5_specialists_month = sorted(
        [{'fullname': k, 'avg_score': v} for k, v in avg_score_by_specialist_month.items()],
        key=lambda x: x['avg_score'], reverse=True
    )[:5]

    message_lines_month = [
        "<b>📊 Аналитика системы за последний месяц:</b>",
        f"📝 <b>Оценок качества:</b> {total_aoq_month}",
        f"⭐ <b>NPS:</b> {total_nps_month}\n",
        "<b>🏆 Топ-5 специалистов по среднему баллу:</b>"
    ]
    for i, spec in enumerate(top_5_specialists_month, start=1):
        message_lines_month.append(f"{i}. <b>{spec['fullname']}</b> — {spec['avg_score']:.2f}")

    if avg_score_by_service_month:
        message_lines_month.append("\n<b>📌 Средний балл по услугам:</b>")
        for name, avg in avg_score_by_service_month.items():
            message_lines_month.append(f"- {name}: {avg:.2f}")

    await bot.send_message(user_tg_id, "\n".join(message_lines_month), parse_mode="HTML")

    # --- АНАЛИТИКА ЗА НЕДЕЛЮ ---
    avg_score_by_specialist_week = {}
    avg_score_by_service_week = {}

    for spec in specialists:
        scores = [aoq.score for aoq in all_aoqs if aoq.specialist_id == spec.id and aoq.created_at >= last_week]
        if scores:
            avg_score_by_specialist_week[spec.fullname] = float(sum(scores)/len(scores))

    for service in services:
        scores = [aoq.score for aoq in all_aoqs if aoq.service_id == service.id and aoq.created_at >= last_week]
        if scores:
            avg_score_by_service_week[service.name] = float(sum(scores)/len(scores))

    total_aoq_week = len([aoq for aoq in all_aoqs if aoq.created_at >= last_week])
    total_nps_week = len([nps for nps in all_nps if nps.created_at >= last_week])

    top_5_specialists_week = sorted(
        [{'fullname': k, 'avg_score': v} for k, v in avg_score_by_specialist_week.items()],
        key=lambda x: x['avg_score'], reverse=True
    )[:5]

    message_lines_week = [
        "<b>📊 Аналитика системы за последнюю неделю:</b>",
        f"📝 <b>Оценок качества:</b> {total_aoq_week}",
        f"⭐ <b>NPS:</b> {total_nps_week}\n",
        "<b>🏆 Топ-5 специалистов по среднему баллу:</b>"
    ]
    for i, spec in enumerate(top_5_specialists_week, start=1):
        message_lines_week.append(f"{i}. <b>{spec['fullname']}</b> — {spec['avg_score']:.2f}")

    if avg_score_by_service_week:
        message_lines_week.append("\n<b>📌 Средний балл по услугам:</b>")
        for name, avg in avg_score_by_service_week.items():
            message_lines_week.append(f"- {name}: {avg:.2f}")

    await bot.send_message(user_tg_id, "\n".join(message_lines_week), parse_mode="HTML")
    
async def send_full_statistics_excel(bot: Bot, user_tg_id: int = None):
    # Получаем все AOQ и NPS с предзагрузкой связей
    aoqs = await aoq_crud.get_list_with_relations()
    nps_list = await nps_crud.get_list_with_relations()

    # Формируем данные для Excel
    aoq_data = []
    for aoq in aoqs:
        aoq_data.append({
            "AOQ ID": aoq.id,
            "Специалист": aoq.specialist.fullname if aoq.specialist else None,
            "Услуга": aoq.service.name if aoq.service else None,
            "Пользователь": aoq.user.full_name if aoq.user else aoq.user.username if aoq.user else None,
            "Социальная категория": aoq.user.socialsubcategory.name if aoq.user and aoq.user.socialsubcategory and aoq.user else None,
            "Score": aoq.score,
            "Комментарий": aoq.comment,
            "Дата": aoq.created_at,
        })

    nps_data = []
    for nps in nps_list:
        nps_data.append({
            "AOQ NAME": nps.aoq.id if nps.aoq else None,
            "Специалист": nps.aoq.specialist.fullname if nps.aoq and nps.aoq.specialist else None,
            "Пользователь": nps.user.full_name if nps.user else nps.user.username if nps.user else None,
            "Score": nps.score,
            "Дата": nps.created_at,
        })
    date = tz_now_naive().date()
    # Создаем Excel в временном файле
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        with pd.ExcelWriter(tmp.name, engine="openpyxl") as writer:
            pd.DataFrame(aoq_data).to_excel(writer, sheet_name="AOQ", index=False)
            pd.DataFrame(nps_data).to_excel(writer, sheet_name="NPS", index=False)

        # Передаем в Telegram как InputFile
        file = FSInputFile(tmp.name, filename=f"full_statistics-{date}.xlsx")
        if user_tg_id:
            await bot.send_document(user_tg_id, file, caption="📊 Полная статистика AOQ и NPS")
        else:
            admins = await user_crud.get_list(role="admin")
            for admin in admins:
                try:
                    await bot.send_document(admin.tg_id, file, caption="📊 Полная статистика AOQ и NPS")
                except Exception as e:
                    print(f"❌ Ошибка при отправке статистики администратору {admin.tg_id}: {e}")
    os.remove(tmp.name)