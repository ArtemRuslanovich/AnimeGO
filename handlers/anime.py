from aiogram import Bot
from aiogram.types import Message
from urllib.parse import quote
from aiogram.fsm.context import FSMContext
from Utils.statesform import Selector
from Utils.anime.search_parser import search_parser
from Utils.form.description_parser import description_parser
from aiogram.enums import ParseMode
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


async def select_anime(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(Selector.FIND_ANIME)
    await message.reply("Напиши что ты хочешь посмотреть, я постараюсь найти")

async def find_anime(message: Message, bot: Bot, state: FSMContext):
    words = message.text.split()
    
    words_joined = " ".join(words)
    
    url = f"https://animego.org/search/all?q={quote(words_joined)}"
    
    search_parsed_result = await search_parser(url)
    parsed_result = search_parsed_result[0]
    async def send_description_message(parsed_result):
        poster_url, title, description, rating, anime_id  = await description_parser(parsed_result)
        message_text = f"<b>{title}</b>\n\n" \
                   f"Рейтинг: {rating}\n" \
                   f"{description}\n" \
                   f"{parsed_result}"
        subscribe_button = InlineKeyboardButton(text="Подписаться", callback_data=f'subscribe_{anime_id}')

    # Создаем клавиатуру и добавляем к ней кнопку
        key_sub = InlineKeyboardMarkup(inline_keyboard=[[subscribe_button]])
        await message.answer_photo(photo=poster_url, caption=message_text, parse_mode=ParseMode.HTML, reply_markup=key_sub)
    await send_description_message(parsed_result)

    await state.clear()
    await state.set_state(Selector.FIRST_CH)