from aiogram import Bot, Dispatcher, types, executor
from defs import *

dp = connect_tg()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    result = add_chat_db(message)

    if result == "Group added":
        keyboard = generate_languages_keyboard()
        await message.reply("Please choose the language:", reply_markup=keyboard)
    else:
        await message.reply(result)

@dp.message_handler(commands=['stop'])
async def stop_chat(message: types.Message):
    response = set_chat_inactive(message)
    await message.reply(response)

@dp.message_handler(commands=['language'])
async def choose_language(message: types.Message):
    keyboard = generate_languages_keyboard()
    await message.answer("Please choose the language:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('language_'))
async def set_chat_language(callback_query: types.CallbackQuery):
    language_id = int(callback_query.data.split("_")[1])
    chat_tg_id = callback_query.message.chat.id

    update_chat_language(chat_tg_id, language_id)
    await dp.bot.answer_callback_query(callback_query.id, text="Language has been set!")
    await dp.bot.edit_message_reply_markup(chat_tg_id, callback_query.message.message_id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)