import os
import yt_dlp
from googleapiclient.discovery import build
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import API_KEY, API_TOKEN
import random
import string
from db import *

create_tables()

youtube = build("youtube", "v3", developerKey=API_KEY)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

def generate_referral_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

def search_youtube(query):
    request = youtube.search().list(q=query, part="snippet", type="video", order="relevance")
    response = request.execute()
    if response["items"]:
        video_id = response["items"][0]["id"]["videoId"]
        return f"https://www.youtube.com/watch?v={video_id}"
    return None

def download_audio(url):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ffmpeg_location': r'C:\ffmpeg\bin\ffmpeg.exe',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return f"downloads/{info['title']}.mp3"

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    referral_code = generate_referral_code()
    
    # Проверяем, есть ли реферальный код
    args = message.get_args()
    referred_by = None
    if args:
        try:
            referred_by = int(args)
        except ValueError:
            pass  

    add_user(user_id, referral_code, referred_by)
    await message.reply("Привет! Отправь название песни, и я скачаю её для тебя.")

@dp.message_handler(commands=['vip'])
async def vip_command(message: types.Message):
    user_id = message.from_user.id
    set_vip_status(user_id, 1)
    await message.reply("Поздравляю! Вы стали VIP пользователем.")

@dp.message_handler(commands=['profile'])
async def profile_command(message: types.Message):
    user_id = message.from_user.id
    profile = get_user_profile(user_id)

    if profile is None:
        await message.reply("Вы ещё не зарегистрированы в системе. Отправьте /start.")
        return

    text = (
        f"👤 *Ваш профиль:*\n"
        f"🆔 ID: `{user_id}`\n"
        f"🌟 Статус: {profile['vip_status']}\n"
        f"👥 Привлечено рефералов: {profile['referrals']}\n"
        f"🎵 Музыка скачана: {profile['download_count']} раз(а)"
    )
    
    await message.reply(text, parse_mode="Markdown")

@dp.message_handler()
async def search_and_download(message: types.Message):
    user_id = message.from_user.id
    query = message.text

    is_vip = get_vip_status(user_id)

    if is_vip:
        video_url = search_youtube(query)
        if video_url:
            file_path = download_audio(video_url)
            increment_download_count(user_id)  
            await message.reply_audio(audio=open(file_path, 'rb'))
            os.remove(file_path)
        else:
            await message.reply("Не нашел видео по вашему запросу.")
    else:
        await message.reply("Вы не являетесь VIP пользователем. Для получения VIP статуса используйте команду /vip")

if __name__ == "__main__":
    os.makedirs("downloads", exist_ok=True)
    executor.start_polling(dp, skip_updates=True)
