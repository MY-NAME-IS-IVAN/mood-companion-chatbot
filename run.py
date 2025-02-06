import asyncio
from openai import OpenAI
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BOT_TOKEN = os.getenv("BOT_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

user_processing = set()
user_conversations = {}

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Hey there! 😊 I’m here to listen, support you, and share insights about yourself that you might not have noticed—but could really help your mental well-being. Feel free to talk to me about anything!')

@dp.message(F.document)
async def document_reply(message: Message):
    await message.reply("Sorry, I can understand only text")

@dp.message(F.text)
async def answer(message: Message):
    user_id = message.from_user.id

    if user_id in user_processing:
        return

    user_processing.add(user_id)

    if user_id not in user_conversations:
        user_conversations[user_id] = [
            {"role": "system", "content": "You are a supportive and empathetic AI designed to help users reflect on their thoughts and emotions. You listen carefully, offer thoughtful insights, and encourage a positive mindset while maintaining a warm and understanding tone. You do not diagnose or provide medical advice but aim to be a comforting and engaging conversation partner."}
        ]

    user_conversations[user_id].append({"role": "user", "content": message.text})

    try:
        sent_message = await message.reply("Thinking...")

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=user_conversations[user_id],
        )

        reply = response.choices[0].message.content
        user_conversations[user_id].append({"role": "assistant", "content": reply})

        await sent_message.edit_text(reply)

    except Exception as e:
        await message.answer("Oops! Something went wrong. Try again later.")
        print(f"OpenAI API Error: {e}")

    finally:
        user_processing.discard(user_id)  # Remove user from "waiting" list


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')