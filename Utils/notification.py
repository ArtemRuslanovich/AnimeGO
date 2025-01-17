import asyncio
import logging
from aiogram import Bot
from utils.postgresdata import connect_to_db, close_db_connection
from datetime import datetime
from bs4 import BeautifulSoup
import aiohttp
from aiogram.enums import ParseMode
from utils.form.description_parser import description_parser
from settings import Settings

    
async def process_anime_list_entry(bot, anime_list_entry):
    try:
        anime_list = anime_list_entry['anime_list']

        if anime_list and isinstance(anime_list, list):
            async with aiohttp.ClientSession() as session:
                for anime_url in anime_list:
                    anime_url = anime_url.replace('_', '-') if anime_url else None
                    async with session.get(f"https://animego.org/anime/{anime_url}") as response:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')

                        date_div = soup.find('div', class_='col-6 col-sm-3 col-md-3 col-lg-3 text-right text-truncate')
                        if date_div:
                            date_str = date_div.text.strip()

                            russian_month_names = {
                                'января': 'January',
                                'февраля': 'February',
                                'марта': 'March',
                                'апреля': 'April',
                                'мая': 'May',
                                'июня': 'June',
                                'июля': 'July',
                                'августа': 'August',
                                'сентября': 'September',
                                'октября': 'October',
                                'ноября': 'November',
                                'декабря': 'December'
                            }
                            for russian_month, english_month in russian_month_names.items():
                                date_str = date_str.replace(russian_month, english_month)

                            date = datetime.strptime(date_str, '%d %B %Y')

                            if date.date() == datetime.today().date():
                                anime_url = anime_url.replace('-', '_') if anime_url else None
                                connection = await connect_to_db()
                                query = "SELECT user_id, anime_list FROM usersdata WHERE $1 = ANY(anime_list);"
                                result = await connection.fetch(query, anime_url)

                                for record in result:
                                    user_id, user_anime_list = record['user_id'], record['anime_list']

                                    if anime_url in user_anime_list:
                                        await send_description_message(bot, anime_url)
    except Exception as e:
        logging.exception(f"An error occurred during processing anime list entry: {e}")

async def send_description_message(bot, anime_url):
    try:
        poster_url, title, description, rating, anime_id = await description_parser(anime_url)
        message_text = f"<b>{title}</b>\n\n" \
                    f"Рейтинг: {rating}\n" \
                    f"{description}\n" \
                    f"{anime_url}"
        await bot.send_photo(photo=poster_url, caption=message_text, parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.exception(f"An error occurred during sending description message: {e}")

async def notification_job():
    try:
        connection = await connect_to_db()
        query = "SELECT anime_list FROM usersdata;"
        result = await connection.fetch(query)

        bot = Bot(token=Settings.bots.bot_token)
        tasks = [process_anime_list_entry(bot, anime_list_entry) for anime_list_entry in result]
        await asyncio.gather(*tasks)
    except Exception as e:
        logging.exception(f"An error occurred: {e}")
    finally:
        await close_db_connection(connection)