import telebot
from googletrans import Translator
import requests
import logging
import sys

# Настройка логирования
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Удаляем все обработчики по умолчанию
logger.handlers = []

# Обработчик для записи логов в файл
file_handler = logging.FileHandler('bot.log', encoding='utf-8')  # Указываем кодировку utf-8 для файла
file_handler.setLevel(logging.INFO)

# Обработчик для вывода логов в консоль (например, в PyCharm)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Используем кодировку utf-8 для консоли
console_handler.setStream(sys.stdout)

# Формат логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Добавляем обработчики в логгер
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Создаем бота, используя ваш токен
TOKEN = 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
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

                # Добавляем все примеры использования, если они есть
                if 'example' in definition:
                    examples.append(definition['example'])

                # Добавляем дополнительные примеры, если они есть
                if 'synonyms' in definition:
                    examples.extend(definition.get('synonyms', []))  # Добавляем дополнительные примеры (если есть)

        return definitions, examples
    else:
        return None, None


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    logger.info(f"User {message.from_user.first_name} started the bot.")
    bot.reply_to(message,
                 "Привет! Введи слово на английском, и я переведу его на русский, добавлю толкование и примеры.")


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def translate_message(message):
    user_message = message.text
    user_id = message.from_user.id
    user_name = message.from_user.first_name

    # Логирование полученного сообщения
    logger.info(f"Received message from {user_name} (ID: {user_id}): {user_message}")

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
        logger.info(f"Sent response to {user_name} (ID: {user_id}): {response_text}")

        # Ответ бота
        bot.reply_to(message, response_text)
    except Exception as e:
        # Логирование ошибки
        logger.error(f"Error occurred while processing message from {user_name} (ID: {user_id}): {e}")
        bot.reply_to(message, "Извините, не удалось выполнить запрос.")
        print(f"Ошибка: {e}")


# Запуск бота
bot.polling()
