# Telegram Voice Bot с OpenAI/OpenRouter

Этот бот позволяет отправлять голосовые и текстовые сообщения в Telegram и получать ответы от языковой модели через OpenRouter API.

## Возможности

- Обработка голосовых сообщений с помощью распознавания речи
- Обработка текстовых сообщений
- Интеграция с различными языковыми моделями через OpenRouter
- Индикатор набора текста во время обработки сообщений
- Логирование всех действий для отладки

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/YOUR_USERNAME/telegram_voice_bot.git
cd telegram_voice_bot
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
pip install -r requirements.txt
```

3. Установите FFmpeg (если еще не установлен):
```bash
# для Ubuntu/Debian
sudo apt-get install ffmpeg

# для macOS
brew install ffmpeg

# для Windows скачайте с официального сайта
```

4. Создайте файл `.env` и заполните его своими данными:
```
# Telegram Bot Token (получить у @BotFather)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token

# OpenRouter API Key (получить на openrouter.ai)
OPENROUTER_API_KEY=your_openrouter_api_key

# AI Model (выберите модель на openrouter.ai)
AI_MODEL=your_chosen_model
```

## Использование

1. Запустите бота:
```bash
python bot.py
```

2. В Telegram найдите вашего бота и отправьте команду `/start`

3. Отправьте голосовое или текстовое сообщение

## Настройка

Вы можете настроить:
- Промпт для языковой модели в файле `config.py`
- Параметры распознавания речи
- Формат временных файлов
- Параметры логирования

## Требования

- Python 3.7+
- FFmpeg
- Доступ к интернету
- Telegram Bot Token
- OpenRouter API Key

## Лицензия

MIT

## Автор

Слова и музыка народные
