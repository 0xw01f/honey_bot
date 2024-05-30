import os
from dotenv import load_dotenv
import sqlite3
from telegram import Update
import telegram
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

load_dotenv()
TLG_TOKEN = os.getenv('TG_BOT_TOKEN')

START_ROUTES, CERT_INFO_TEXTE = range(2)

# SQLite3 database connection
conn = sqlite3.connect('user_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users 
             (user_id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, username TEXT, phone_number TEXT, language_code TEXT)''')
conn.commit()


async def start(update: Update, context: CallbackContext) -> None:

    # Ask the user to share their contact
    chat_id = update.message.chat_id
    bot = context.bot
    contact_keyboard = telegram.KeyboardButton(text="🪄 Share contact", request_contact=True)
    custom_keyboard = [[ contact_keyboard ]]

    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True, one_time_keyboard=True)
    await bot.send_message(chat_id=chat_id, 
                      text="🎁 Would you mind sharing your contact with me?", 
                      reply_markup=reply_markup)
    return START_ROUTES


async def contact(update: Update, context: CallbackContext) -> None:
    # Get the contact info from the message available without asking
    chat_id = update.message.chat_id
    bot = context.bot
    user = update.message.from_user
    contact = update.message.contact
    username = user.username
    phone_number = contact.phone_number
    first_name = user.first_name
    last_name = user.last_name
    language_code = user.language_code

    print(f"User {user.id} ({first_name} {last_name}) shared their contact info: {phone_number}")

    # Store all the information in the database
    c.execute("INSERT OR REPLACE INTO users (user_id, first_name, last_name, username, phone_number, language_code) VALUES (?, ?, ?, ?, ?, ?)", (user.id, first_name, last_name, username, phone_number, language_code))
    conn.commit()
    

    await bot.send_message(chat_id=chat_id, text=f"""
    Thank you !
This is the information I received from you:
    First name: {first_name}
    Last name: {last_name}
    Username: {username}
    Phone number: {phone_number}
    Language code: {language_code}
    """)
  
    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    application = (
        Application.builder()
        .token(TLG_TOKEN)
        .arbitrary_callback_data(True)
        .build()
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                MessageHandler(filters.CONTACT, contact),
            ]
        },
        fallbacks=[CommandHandler("start", start)],
    )
   

    application.add_handler(conv_handler)
   
    application.run_polling()



if __name__ == '__main__':
    main()
