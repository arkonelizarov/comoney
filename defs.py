import logging
import sqlite3
from aiogram import Bot, Dispatcher

DB_FILE = 'db.db'

def connect_db():
    return sqlite3.connect(DB_FILE)

def get_tg_api_key():
    with connect_db() as connection:
        cursor = connection.cursor()
        api_key = cursor.execute("select value from settings where name='telegram_bot_api_key_qa';").fetchone()[0]
    return api_key

def connect_tg():
    logging.basicConfig(level=logging.INFO)
    API_TOKEN = get_tg_api_key()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot)
    return dp

def add_chat_db(message):
    with connect_db() as connection:
        cursor = connection.cursor()

        chat_tg_id = message.chat.id
        chat_title = message.chat.title

        cursor.execute("SELECT chat_id FROM chats WHERE chat_tg_id=?", (chat_tg_id,))
        existing_chat = cursor.fetchone()

        if existing_chat is None:
            cursor.execute("INSERT INTO chats (chat_title, chat_active, chat_tg_id) VALUES (?, ?, ?)",
                               (chat_title, True, chat_tg_id))
            ret = "Group added"
        else:
            cursor.execute("UPDATE chats SET chat_title=?, chat_active=? WHERE chat_tg_id=?",
                           (chat_title, True, chat_tg_id))
            ret = "Group updated"

        connection.commit()

    return ret

def set_chat_inactive(message):
    with connect_db() as connection:
        cursor = connection.cursor()

        chat_tg_id = message.chat.id

        cursor.execute("SELECT chat_id FROM chats WHERE chat_tg_id=?", (chat_tg_id,))
        existing_chat = cursor.fetchone()

        if existing_chat is None:
            chat_title = message.chat.title
            cursor.execute("INSERT INTO chats (chat_title, chat_active, chat_tg_id) VALUES (?, ?, ?)",
                               (chat_title, False, chat_tg_id))
            ret = "Group added and disabled"
        else:
            cursor.execute("UPDATE chats SET chat_active=? WHERE chat_tg_id=?", (False, chat_tg_id))
            ret = "Group disabled"

        connection.commit()
    return ret


from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_languages():
    with connect_db() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT language_id, name_en FROM languages")
        languages = cursor.fetchall()
    return languages

def generate_languages_keyboard():
    languages = get_languages()
    keyboard = InlineKeyboardMarkup(row_width=2)
    for language in languages:
        language_id, name_en = language
        keyboard.add(InlineKeyboardButton(text=name_en, callback_data=f"language_{language_id}"))
    return keyboard

def update_chat_language(chat_tg_id: int, language_id: int):
    with connect_db() as connection:
        cursor = connection.cursor()
        cursor.execute("UPDATE chats SET language_id=? WHERE chat_tg_id=?", (language_id, chat_tg_id))
        connection.commit()