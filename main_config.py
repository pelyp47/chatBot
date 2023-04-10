from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

#bot config
TOKEN_API="6204898530:AAGobrG91GkYLfGVqCg3WSM__3XhLmsF2H8"
bot = Bot(TOKEN_API)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

owner_id = 6201337905
