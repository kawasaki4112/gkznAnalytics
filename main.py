import os, sys
import asyncio
import colorama
import logging

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.data.models import tz

from src.data.db import init_db
from src.middlewares import register_all_middlwares
from src.routers import register_all_routers
from src.utils.misc_functions import backup_db, send_full_statistics_excel
from src.utils.misc.bot_commands import set_commands
from src.utils.misc.bot_logging import bot_logger

load_dotenv(override=True)

BOT_SCHEDULER = AsyncIOScheduler(timezone=tz)

async def scheduler_start(bot: Bot):
    # BOT_SCHEDULER.add_job(update_profit_month, trigger="cron", day=1, hour=00, minute=00, second=5)
    # BOT_SCHEDULER.add_job(update_profit_week, trigger="cron", day_of_week="mon", hour=00, minute=00, second=10)
    # BOT_SCHEDULER.add_job(update_profit_day, trigger="cron", hour=00, minute=00, second=15, args=(bot,))
    BOT_SCHEDULER.add_job(backup_db, trigger="cron", hour=00, args=(bot,))
    BOT_SCHEDULER.add_job(send_full_statistics_excel, day_of_week="mon", trigger="cron", hour=12, minute=00, args=(bot,))
    # BOT_SCHEDULER.add_job(check_update, trigger="cron", hour=00, args=(bot, arSession,))
    # BOT_SCHEDULER.add_job(check_mail, trigger="cron", hour=12, args=(bot, arSession,))


async def main():
    BOT_SCHEDULER.start()
    await init_db()
    
    dp = Dispatcher()
    bot = Bot(token=os.getenv('TOKEN'))
    register_all_middlwares(dp)
    register_all_routers(dp)
    
    await set_commands(bot)
    await scheduler_start(bot)
    
    bot_logger.warning("BOT WAS STARTED")
    print(colorama.Fore.LIGHTYELLOW_EX + f"~~~~~ Bot was started - @{(await bot.get_me()).username} ~~~~~")
    print(colorama.Fore.LIGHTBLUE_EX + "~~~~~ TG developer - @arsan_duolaj ~~~~~")
    print(colorama.Fore.RESET)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        bot_logger.warning("Bot was stopped")
    finally:
        if sys.platform.startswith("win"):
            os.system("cls")
        else:
            os.system("clear")