import asyncio
import logging
import os
import base64
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import BufferedInputFile
from dotenv import load_dotenv

# Загружаем переменные (Токен)
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Настройки SD (Forge)
SD_URL = "http://127.0.0.1:7861/sdapi/v1/txt2img"

# Инициализация
logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Напиши мне промпт (на английском), и я сгенерирую картинку.")


@dp.message(F.text)
async def handle_prompt(message: types.Message):
    prompt = message.text
    await message.answer(f"🎨 Начинаю рисовать: {prompt} \n⏳ Подожди немного...")

    # Параметры генерации
    payload = {
        "prompt": prompt,
        "steps": 20,
        "width": 512,  # Можно 832 или 1024 для XL/Pony моделей
        "height": 768,
        "cfg_scale": 7
    }

    try:
        # Отправляем запрос в Forge (синхронно, для простоты)
        response = requests.post(SD_URL, json=payload)

        if response.status_code == 200:
            r = response.json()
            # Forge отдает картинку как строку base64, декодируем её
            image_data = base64.b64decode(r['images'][0])

            # Отправляем в Telegram
            photo = BufferedInputFile(image_data, filename="image.png")
            await message.answer_photo(photo, caption=f"✨ Готово: {prompt}")
        else:
            await message.answer(f"Ошибка API: {response.status_code}")

    except Exception as e:
        await message.answer(f"Произошла ошибка подключения: {e}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())