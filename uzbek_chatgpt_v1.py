import logging
import openai
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import TelegramError
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve environment variables
openai_api_key = os.getenv('OPENAI_API_KEY')
telegram_token = os.getenv('TELEGRAM_TOKEN')

# OpenAI API key
openai.api_key = openai_api_key

system = [{"role": "system", "content": "You are Jbot, a helpful AI assistant."}]
user = [{"role": "user", "content": "introduce Jbot"}]
chat = []


# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Function to handle /start command
def start(update, context):
    try:
        update.message.reply_text('Salom! Men ChatGPT botman. Menga xabar yuboring va men javob beraman.')
    except TelegramError as e:
        logger.error(f'Telegram xatosi: {e.message}')
    except Exception as e:
        logger.error(f'Kutilmagan xato: {e}')

# Function to handle /capabilities command (ChatGPT nimalar qila oladi?)
def capabilities(update, context):
    try:
        update.message.reply_text(
            'ChatGPT quyidagi ishlarni bajarishga qodir:\n\n'
            '1. Turli mavzularda matnli javoblar berish.\n'
            '2. Yozuvchi va tahrirlovchi sifatida xizmat qilish.\n'
            '3. Turli tillardagi matnlarni tarjima qilish.\n'
            '4. Ta\'limiy materiallar yaratish va tushuntirish.\n'
            '5. Turli maslahat va tavsiyalar berish.\n'
            '6. Dasturlash bilan bog\'liq maslahatlar berish.\n'
            '7. O\'yinlar va puzzllar yaratish.\n'
            '8. Ro\'zg\'or maslahatlari berish.\n\n'
            'Eslatma: Ba\'zi cheklovlar mavjud.')
    except TelegramError as e:
        logger.error(f'Telegram xatosi: {e.message}')
    except Exception as e:
        logger.error(f'Kutilmagan xato: {e}')

def handle_chatgpt_interaction(update, context):
    user_input = update.message.text
    while user[0]['content'] != "exit":
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Specify the model here
                messages=system + chat[-20:] + user,
                max_tokens=1000,
                top_p=0.9
            )
        except Exception as err:
            print(f"Unexpected {err=}, {type(err)=}")
            raise

    reply = response.choices[0].message['content']
    print(reply)
    
    chat.append({"role": "user", "content": user[0]['content']})
    chat.append({"role": "assistant", "content": reply})
    
    user_input = input("\nPrompt: ")
    user = [{"role": "user", "content": user_input}]

# Function to handle messages
def handle_message(update, context):
    try:
        user_message = update.message.text
        chatbot_response = get_chatgpt_response(user_message)
        update.message.reply_text(chatbot_response)
    except TelegramError as e:
        logger.error(f'Telegram xatosi: {e.message}')
    except Exception as e:
        logger.error(f'Kutilmagan xato: {e}')
        update.message.reply_text("Kechirasiz, men xatolikka uchradim.")

# Function to get response from ChatGPT
def get_chatgpt_response(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "Siz yordamchi assistentsiz."}, 
                      {"role": "user", "content": message}]
        )
        return response.choices[0].message['content']
    except openai.APIError as e:  # Correctly reference the OpenAI Error
        logger.error(f'OpenAI API error: {e}')
        return "So'rovni qayta ishlashda qiyinchiliklar mavjud."
    except Exception as e:
        logger.error(f'Kutilmagan xato: {e}')
        return "Kutilmagan xato yuz berdi."

# Main function to run the bot
def main():
    # Replace with your actual server details for webhook setup
    updater = Updater(telegram_token, use_context=True)
    dp = updater.dispatcher

    # Register handlers
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("capabilities", capabilities))  # New handler for /capabilities
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_chatgpt_interaction))

    # Uncomment the following lines if you're using webhooks
    # updater.start_webhook(listen="0.0.0.0",
    #                       port=8443,
    #                       url_path=telegram_token,
    #                       webhook_url='https://your_domain.com:8443/' + telegram_token)

    # If using polling instead of webhooks, uncomment the next line
    updater.start_polling()

    updater.idle()

if __name__ == '__main__':
    main()