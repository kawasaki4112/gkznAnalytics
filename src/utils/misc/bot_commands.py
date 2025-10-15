# - *- coding: utf- 8 - *-
from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault

from src.data.repositories.user_repository import user_crud

user_commands = [
    BotCommand(command='start', description='♻️ Перезапустить бота'),
    BotCommand(command='cancel_input', description='❌ Отменить ввод'),
]

admin_commands = [
    BotCommand(command='start', description='♻️ Перезапустить бота'),
    BotCommand(command='cancel_input', description='❌ Отменить ввод'),
    BotCommand(command='myid', description='🆔 Узнать свой ID'),
]


async def set_commands(bot: Bot):
    await bot.set_my_commands(user_commands, scope=BotCommandScopeDefault())
    admins = await user_crud.get_list(role="admin")
    for admin in admins:
        try:
            await bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin.tg_id))
        except:
            ...
