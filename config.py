import os
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# API ключи
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Настройки OpenRouter
OPENROUTER_API_BASE = os.getenv("OPENROUTER_API_BASE", "https://openrouter.ai/api/v1")
AI_MODEL = os.getenv("AI_MODEL")

# Промпт для ИИ
AI_PROMPT = """Вы — дружелюбный и полезный ассистент. Ваша задача — помогать пользователям, отвечая на их вопросы и поддерживая беседу.

Особенности общения:
- Будьте вежливы и дружелюбны
- Давайте четкие и понятные ответы
- Если вопрос неясен, уточните детали
- Если не знаете ответ, честно признайтесь в этом
- Старайтесь быть полезным и информативным

Помните:
- Безопасность и этичность прежде всего
- Уважайте личные границы
- Не давайте советов в областях, где требуется профессиональная консультация
- Будьте объективны и непредвзяты"""

# Сообщения бота
MESSAGES = {
    "start": "Привет! Я бот, который может обрабатывать голосовые сообщения и общаться с помощью ИИ. "
             "Просто отправь мне голосовое сообщение или напиши текст, и я отвечу!",
    "error": "Извините, произошла ошибка при обработке вашего сообщения.",
}

# Настройки распознавания речи
SPEECH_RECOGNITION = {
    "language": "ru-RU",
    "timeout": 5,
    "phrase_timeout": 10,
}

# Настройки временных файлов
TEMP_FILES = {
    "voice_extension": ".ogg",
    "wav_extension": ".wav",
    "file_prefix": "voice_",
} 