import os
import logging
import json
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import speech_recognition as sr
from pydub import AudioSegment
from openai import OpenAI
from config import (
    TELEGRAM_BOT_TOKEN,
    OPENROUTER_API_KEY,
    OPENROUTER_API_BASE,
    AI_MODEL,
    AI_PROMPT,
    MESSAGES,
    SPEECH_RECOGNITION,
    TEMP_FILES
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация OpenAI с OpenRouter
client = OpenAI(
    base_url=OPENROUTER_API_BASE,
    api_key=OPENROUTER_API_KEY
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    logger.info(f"Получена команда /start от пользователя {update.effective_user.id}")
    await update.message.reply_text(MESSAGES["start"])

def extract_response_text(response):
    """Извлекает текст ответа из различных форматов ответа API"""
    try:
        # Проверяем наличие ошибки
        if hasattr(response, 'error') and response.error:
            error_msg = f"Ошибка API: {response.error.get('message', 'Неизвестная ошибка')}"
            if 'metadata' in response.error and 'raw' in response.error['metadata']:
                try:
                    raw_error = json.loads(response.error['metadata']['raw'])
                    if 'error' in raw_error and 'message' in raw_error['error']:
                        error_msg = f"Ошибка: {raw_error['error']['message']}"
                except:
                    pass
            logger.error(error_msg)
            return f"Извините, возникла проблема с сервисом AI: {error_msg}"
            
        # Проверяем различные форматы ответа
        if hasattr(response, 'choices') and response.choices:
            return response.choices[0].message.content
        elif hasattr(response, 'content'):
            return response.content
        elif hasattr(response, 'text'):
            return response.text
        elif type(response) is dict:
            if 'choices' in response and response['choices']:
                return response['choices'][0]['message']['content']
            elif 'content' in response:
                return response['content']
        elif type(response) is str:
            return response
        
        # Если ничего не подошло
        logger.error(f"Неизвестный формат ответа: {response}")
        return "Извините, я не смог обработать ответ от сервиса AI."
        
    except Exception as e:
        logger.error(f"Ошибка при извлечении текста ответа: {e}", exc_info=True)
        return "Извините, произошла ошибка при обработке ответа."

async def keep_typing(chat):
    """Поддерживает статус 'печатает' в чате"""
    logger.info("Запущена задача поддержания статуса печати")
    counter = 0
    while True:
        try:
            await chat.send_chat_action(action="typing")
            counter += 1
            logger.info(f"Отправлен статус печати #{counter}")
            # Уменьшаем интервал до 1 секунды для более частого обновления
            await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Задача поддержания статуса печати отменена")
            break
        except Exception as e:
            logger.error(f"Ошибка при отправке статуса печати: {e}")
            break
    logger.info("Задача поддержания статуса печати завершена")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    logger.info(f"Получено текстовое сообщение от пользователя {update.effective_user.id}")
    typing_task = None
    try:
        # Получаем текст сообщения
        text = update.message.text
        logger.info(f"Полученный текст: {text}")
        
        # Сначала отправляем статус печати напрямую
        await update.message.chat.send_chat_action(action="typing")
        
        # Запускаем задачу поддержания статуса печати
        typing_task = asyncio.create_task(keep_typing(update.message.chat))
        
        # Отправляем текст в OpenRouter
        logger.info("Отправка запроса в OpenRouter")
        logger.info(f"Используемая модель: {AI_MODEL}")
        logger.info(f"Используемый промпт: {AI_PROMPT}")
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": AI_PROMPT},
                {"role": "user", "content": text}
            ]
        )
        logger.info("Получен ответ от OpenRouter")
        
        # Логируем структуру ответа
        logger.info(f"Структура ответа: {response}")
        
        # Извлекаем текст ответа и отправляем пользователю
        response_text = extract_response_text(response)
        
        # Отменяем задачу печати перед отправкой ответа
        if typing_task and not typing_task.done():
            logger.info("Отмена задачи поддержания статуса печати")
            typing_task.cancel()
        
        await update.message.reply_text(response_text)
        
    except Exception as e:
        logger.error(f"Ошибка при обработке текстового сообщения: {e}", exc_info=True)
        if typing_task and not typing_task.done():
            typing_task.cancel()
        await update.message.reply_text(MESSAGES["error"])

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик голосовых сообщений"""
    logger.info(f"Получено голосовое сообщение от пользователя {update.effective_user.id}")
    typing_task = None
    try:
        # Получаем голосовое сообщение
        voice_file = await update.message.voice.get_file()
        voice_path = f"{TEMP_FILES['file_prefix']}{update.message.message_id}{TEMP_FILES['voice_extension']}"
        
        # Сначала отправляем статус печати напрямую
        await update.message.chat.send_chat_action(action="typing")
        
        # Запускаем задачу поддержания статуса печати
        typing_task = asyncio.create_task(keep_typing(update.message.chat))
        
        logger.info(f"Скачивание голосового файла: {voice_path}")
        # Скачиваем файл
        await voice_file.download_to_drive(voice_path)
        
        # Обновляем статус печати напрямую перед длительной операцией
        await update.message.chat.send_chat_action(action="typing")
        
        # Конвертируем .ogg в .wav
        audio = AudioSegment.from_ogg(voice_path)
        wav_path = f"{TEMP_FILES['file_prefix']}{update.message.message_id}{TEMP_FILES['wav_extension']}"
        logger.info(f"Конвертация в WAV: {wav_path}")
        audio.export(wav_path, format="wav")
        
        # Обновляем статус печати напрямую перед длительной операцией
        await update.message.chat.send_chat_action(action="typing")
        
        # Распознаем речь
        logger.info("Начало распознавания речи")
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(
                audio_data,
                language=SPEECH_RECOGNITION["language"]
            )
        logger.info(f"Распознанный текст: {text}")
        
        # Обновляем статус печати напрямую перед длительной операцией
        await update.message.chat.send_chat_action(action="typing")
        
        # Отправляем текст в OpenRouter
        logger.info("Отправка запроса в OpenRouter")
        logger.info(f"Используемая модель: {AI_MODEL}")
        logger.info(f"Используемый промпт: {AI_PROMPT}")
        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[
                {"role": "system", "content": AI_PROMPT},
                {"role": "user", "content": text}
            ]
        )
        logger.info("Получен ответ от OpenRouter")
        
        # Логируем структуру ответа
        logger.info(f"Структура ответа: {response}")
        
        # Извлекаем текст ответа и отправляем пользователю
        response_text = extract_response_text(response)
        
        # Отменяем задачу печати перед отправкой ответа
        if typing_task and not typing_task.done():
            logger.info("Отмена задачи поддержания статуса печати")
            typing_task.cancel()
        
        await update.message.reply_text(response_text)
        
        # Удаляем временные файлы
        os.remove(voice_path)
        os.remove(wav_path)
        logger.info("Временные файлы удалены")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке голосового сообщения: {e}", exc_info=True)
        if typing_task and not typing_task.done():
            typing_task.cancel()
        await update.message.reply_text(MESSAGES["error"])

def main():
    """Запуск бота"""
    logger.info("Запуск бота...")
    logger.info(f"Используется модель: {AI_MODEL}")
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    # Запускаем бота
    logger.info("Бот запущен и готов к работе")
    application.run_polling()

if __name__ == '__main__':
    main() 