import time
import threading
import logging
from telebot import TeleBot, types
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from requests.exceptions import ReadTimeout, ConnectionError

# Enable logging for debugging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Replace 'YOUR_BOT_TOKEN' with the token you got from BotFather
TELEGRAM_BOT_TOKEN = '7072264889:AAErhEQp7UlQUPHYEXh1K6UfO8EoKIVqeVA'
bot = TeleBot(TELEGRAM_BOT_TOKEN)

# Store user data
user_data = {}

def start(message):
    bot.reply_to(message, 'Send me a URL and a price alert value in the format: URL, AlertValue')

def handle_message(message):
    text = message.text
    try:
        url, alert_value = text.split(',')
        alert_value = float(alert_value.strip())
        chat_id = message.chat.id
        
        # Store user data
        user_data[chat_id] = {
            'url': url.strip(),
            'alert_value': alert_value,
            'chat_id': chat_id
        }
        
        bot.reply_to(message, f'Got it! I will alert you when the price goes below {alert_value}.')
        
        # Schedule the price check job
        schedule_price_check(chat_id)
    except ValueError:
        bot.reply_to(message, 'Please provide the URL and alert value in the correct format: URL, AlertValue')

def schedule_price_check(chat_id):
    def job():
        while True:
            check_price(chat_id)
            time.sleep(3600)  # Check every hour
    
    thread = threading.Thread(target=job)
    thread.start()

def check_price(chat_id):
    user_info = user_data.get(chat_id)
    if not user_info:
        return
    
    url = user_info['url']
    alert_value = user_info['alert_value']
    
    try:
        d = webdriver.Chrome()
        d.get(url)
        try:
            price = int(d.find_elements(By.CLASS_NAME, 'a-price-whole')[-1].text.replace(',', ''))
        except NoSuchElementException:
            bot.send_message(chat_id, 'Error parsing the price from the page.')
            return
        finally:
            d.quit()
        
        if price < alert_value:
            bot.send_message(chat_id, f'The price has dropped to ₹{price}!\n{url}')
        else:
            bot.send_message(chat_id, f'The current price is ₹{price}. Waiting for it to drop below ₹{alert_value}.')
    
    except WebDriverException as e:
        logger.error(f"WebDriverException occurred: {e}")
        bot.send_message(chat_id, 'Error fetching the price from the page.')
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        bot.send_message(chat_id, 'An unexpected error occurred while checking the price.')

# Handlers
@bot.message_handler(commands=['start'])
def on_start(message):
    start(message)

@bot.message_handler(func=lambda message: True)
def on_message(message):
    handle_message(message)

if __name__ == '__main__':
    while True:
        try:
            bot.polling()
        except (ReadTimeout, ConnectionError) as e:
            logger.error(f"Network error occurred: {e}")
            time.sleep(15)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            time.sleep(15)

