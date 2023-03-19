import asyncio

from aiogram.utils import executor
from loader import bot, dp
from handlers.client import register_message_handler_client, scheduler

register_message_handler_client(dp)


async def on_startup(dp):
    print('Вы онлайн!')
    asyncio.create_task(scheduler())


if __name__ == "__main__":
    executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
