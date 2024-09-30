import telebot
from googletrans import Translator
import requests
import logging

# Настройка логирования
logging.basicConfig(
    filename='bot.log',  # Файл для логирования
    level=logging.INFO,  # Уровень логирования
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  # Формат логов
)

# Создаем бота, используя ваш токен
TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
bot = telebot.TeleBot(TOKEN)

# Создаем экземпляр переводчика
translator = Translator()

# Функция для получения толкования и примеров использования через DictionaryAPI
def get_word_info(word):
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        definitions = []
        examples = []

        # Извлекаем определение и примеры использования
        for meaning in data[0]['meanings']:
            for definition in meaning['definitions']:
                definitions.append(definition['definition'])
                if 'example' in definition:
                    examples.append(definition['example'])

        return definitions, examples
    else:
        return None, None


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    logging.info(f"User {message.from_user.first_name} started the bot.")
    bot.reply_to(message,
                 "Привет! Введи слово на английском, и я переведу его на русский, добавлю толкование и примеры.")


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def translate_message(message):
    user_message = message.text
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Логирование полученного сообщения
    logging.info(f"Received message from {user_name} (ID: {user_id}): {user_message}")

    # Пытаемся перевести сообщение с английского на русский
    try:
        translation = translator.translate(user_message, src='en', dest='ru')
        translated_text = translation.text

        # Получаем толкование и примеры использования слова
        definitions, examples = get_word_info(user_message)

        if definitions:
            definition_text = '\n'.join([f"{i + 1}. {d}" for i, d in enumerate(definitions)])
        else:
            definition_text = "Толкование не найдено."

        if examples:
            examples_text = '\n'.join([f"{i + 1}. {ex}" for i, ex in enumerate(examples)])
        else:
            examples_text = "Примеры использования не найдены."

        # Формируем ответ
        response_text = (
            f"Перевод: {translated_text}\n\nТолкование:\n{definition_text}\n\nПримеры использования:\n{examples_text}"
        )

        # Логирование ответа
        logging.info(f"Sent response to {user_name} (ID: {user_id}): {response_text}")

        # Ответ бота
        bot.reply_to(message, response_text)
    except Exception as e:
        # Логирование ошибки
        logging.error(f"Error occurred while processing message from {user_name} (ID: {user_id}): {e}")
        bot.reply_to(message, "Извините, не удалось выполнить запрос.")
        print(f"Ошибка: {e}")


# Запуск бота
bot.polling()
