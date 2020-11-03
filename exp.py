import asyncio
import os
from constants import *
from aiogram.utils import executor
from urllib import parse

from allen import  Scrap
import logging
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types.reply_keyboard import  ReplyKeyboardRemove
from aiogram import Bot, Dispatcher, executor, types
API_TOKEN = os.environ.get("BOT_TOKEN")
AllenMarkup = InlineKeyboardMarkup()
AllenMarkup.add(InlineKeyboardButton("Live",callback_data="live"),InlineKeyboardButton("Digital",callback_data="digital"),InlineKeyboardButton("Cancel",callback_data="cancel"))
# Configure logging
logging.basicConfig(level=logging.INFO)
# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command
    """
    await message.reply("Hi!\nI'm Vector! \n try typing /help")

@dp.message_handler(commands=['help'])
async def help(message: types.Message):
    """
    This handler will be called when user sends `/help` command
    """
    await message.answer("only one command /allen \n more coming soon")


@dp.message_handler(commands=["allen"])
async def allen(message: types.Message):
    await message.answer("Live or Digital",reply_markup=AllenMarkup)

@dp.message_handler(commands=["remove"])
async def remove(message: types.Message):
    await message.answer(ReplyKeyboardRemove(),reply_markup=ReplyKeyboardRemove())
@dp.message_handler(commands=["reload"])
async def reloadVars(message: types.Message):
    await message.answer("Reloaded")


@dp.message_handler()
async def echo(message: types.Message):
    if message.is_command():
        await message.answer("There is no such Command Try using /help")
    else:
        await message.answer("ML chatbot is currently under work")

def toMarkup(links_list):
    markup = InlineKeyboardMarkup()
    for link in links_list:
        if link.linkType == "url":
            markup.add(InlineKeyboardButton(link.name,url=link.url))
        elif link.linkType == "data":
            markup.add(InlineKeyboardButton(link.name,callback_data=link.url))
        else:
            logging.warning("Markup not succesful invalid link type")
    return markup

@dp.callback_query_handler()
async def callback(callback_query: types.CallbackQuery):
    if callback_query.data=="live":
        await asyncio.gather(callback_query.answer("Scraping Live Links"),callback_query.message.edit_reply_markup(None),callback_query.message.edit_text("Scraping ..."))

        ans = await Scrap().allLive()
        markup = toMarkup(ans)
        await  asyncio.gather(callback_query.message.edit_text("These are the links"),callback_query.message.edit_reply_markup(markup))
        
    elif callback_query.data=="digital":
        try:
            await asyncio.gather(callback_query.answer("Scraping Live Links"),callback_query.message.edit_reply_markup(None),callback_query.message.edit_text("Scraping ..."))
        except:
            await callback_query.answer("An error occured try again")
        ans = await Scrap().allDigital()
        markup = toMarkup(ans)
        
        await  asyncio.gather(callback_query.message.edit_text("Select one of these"),callback_query.message.edit_reply_markup(markup))

    elif callback_query.data=="cancel":
        
        await asyncio.gather(callback_query.message.edit_reply_markup(None),callback_query.message.edit_text("Cancelled"))

    elif callback_query.data and callback_query not in ["cancel", "digital", "live"]:
        url = parse.urljoin(DIGITAL_MODULE_PATH,callback_query.data)
        ans = await Scrap().digital(url)
        if type(ans) is str:
            await  asyncio.gather(callback_query.message.edit_text(ans))
            return
        print(ans)
        markup = toMarkup(ans)
        await  asyncio.gather(callback_query.message.edit_text("These are the links"),callback_query.message.edit_reply_markup(markup))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)