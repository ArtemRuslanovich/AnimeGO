import pytest
from aiogram import Bot
from utils.settings import Settings
from utils.notification import process_anime_list_entry


@pytest.mark.asyncio
async def test_process_anime_list_entry():
    # Создайте виртуальные данные для теста, например, используя pytest fixtures
    anime_list_entry = {'anime_list': ['anime_url_1', 'anime_url_2']}

    # Вместо bot вы можете использовать мок-объект или как-то иначе обработать его в тестах
    bot = Bot(token=Settings.bots.bot_token)

    # Вызовите вашу асинхронную функцию и дождитесь её завершения
    await process_anime_list_entry(bot, anime_list_entry)