import os
import asyncio
import colorama

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from src.data.db import init_db
from src.middlewares import register_all_middlwares
from src.routers import register_all_routers
from src.utils.misc.bot_logging import bot_logger

load_dotenv(override=True)

async def main():
    await init_db()
    
    dp = Dispatcher()
    bot = Bot(token=os.getenv('TOKEN'))
    register_all_middlwares(dp)
    register_all_routers(dp)
    
    bot_logger.warning("BOT WAS STARTED")
    print(colorama.Fore.LIGHTYELLOW_EX + f"~~~~~ Bot was started - @{(await bot.get_me()).username} ~~~~~")
    print(colorama.Fore.LIGHTBLUE_EX + "~~~~~ TG developer - @arsan_duolaj ~~~~~")
    print(colorama.Fore.RESET)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())