# bot.py
import telebot
import yt_dlp
import os
import re
from yt_dlp.utils import DownloadError, ExtractorError
from config import TOKEN, DOWNLOAD_DIR

bot = telebot.TeleBot(TOKEN)

user_sessions = {}

def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_', name)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message,
        "🤖 Привет!\n"
        "• Пришлите ссылку на YouTube — выберу качество или аудио.\n"
        "• Или используйте: /search <запрос>"
    )

@bot.message_handler(commands=['search'])
def search_youtube(message):
    query = message.text[8:].strip()
    chat_id = message.chat.id
    print(f"[LOG] Получена команда /search от {chat_id}: '{query}'")
    
    if not query:
        bot.reply_to(message, "🔍 Используйте: /search <запрос>")
        print("[LOG] Пустой запрос — отмена.")
        return

    try:
        sent_init = bot.send_message(chat_id, "🔍 Ищу... (это займёт 5-10 сек)")
        print(f"[LOG] Отправлено 'Ищу...' (msg_id={sent_init.message_id})")
        
        ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'socket_timeout': 20,
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"[LOG] Запуск полного поиска: ytsearch10:{query}")
            result = ydl.extract_info(f"ytsearch10:{query}", download=False)
            videos = []
            entries = result.get('entries', []) if result else []
            
            for entry in entries[:10]:
                if not entry:
                    continue
                url = entry.get('webpage_url')
                title = entry.get('title') or 'Без названия'
                uploader = entry.get('uploader') or 'Неизвестен'
                duration = entry.get('duration') or 0
                if url:
                    videos.append({
                        'url': url,
                        'title': title,
                        'uploader': uploader,
                        'duration': duration
                    })

            print(f"[LOG] Найдено видео: {len(videos)}")

        if not videos:
            bot.send_message(chat_id, "❌ Ничего не найдено.")
            print("[LOG] Результаты отсутствуют.")
            return

        markup = telebot.types.InlineKeyboardMarkup()
        for i, v in enumerate(videos):
            title_clean = sanitize_filename(v['title'])
            uploader = v['uploader']
            duration_sec = int(v['duration']) if v['duration'] else 0
            mins, secs = divmod(duration_sec, 60)
            btn_text = f"{uploader[:15]}: {title_clean[:25]}... ({mins}:{secs:02d})"
            markup.add(telebot.types.InlineKeyboardButton(
                btn_text,
                callback_data=f"search:{v['url']}"
            ))
            print(f"[LOG] Кнопка {i+1}: {uploader}: {title_clean[:40]}...")

        sent = bot.send_message(chat_id, "🔎 Результаты поиска:", reply_markup=markup)
        user_sessions[chat_id] = {'bot_messages': [sent_init.message_id, sent.message_id]}
        print(f"[LOG] Сообщение с результатами отправлено (msg_id={sent.message_id})")

    except Exception as e:
        error_detail = f"{type(e).__name__}: {str(e)}"
        bot.send_message(chat_id, f"❌ Ошибка поиска: {str(e)[:150]}")
        print(f"[ERROR] Поиск упал: {error_detail}")

@bot.message_handler(func=lambda m: 'youtube.com' in m.text or 'youtu.be' in m.text)
def handle_youtube_link(message):
    url = message.text.strip()
    _show_download_options(message, url)

def _show_download_options(message, url):
    chat_id = message.chat.id
    if chat_id in user_sessions:
        for msg_id in user_sessions[chat_id].get('bot_messages', []):
            try:                bot.delete_message(chat_id, msg_id)
            except:
                pass

    markup = _get_quality_markup()

    sent = bot.reply_to(message, "🎥 Выберите формат:", reply_markup=markup)
    user_sessions[chat_id] = {
        'url': url,
        'bot_messages': [sent.message_id]
    }

def _show_download_options_by_chat_id(chat_id, url):
    if chat_id in user_sessions:
        for msg_id in user_sessions[chat_id].get('bot_messages', []):
            try:
                bot.delete_message(chat_id, msg_id)
            except:
                pass
              
    markup = _get_quality_markup()

    sent = bot.send_message(chat_id, "🎥 Выберите формат:", reply_markup=markup)
    user_sessions[chat_id] = {
        'url': url,
        'bot_messages': [sent.message_id]
    }

@bot.callback_query_handler(func=lambda call: True)
def handle_choice(call):
    chat_id = call.message.chat.id
    data = call.data
    print(f"[LOG] Callback от {chat_id}: '{data}'")
    
    if data.startswith("search:"):
        url = data[7:]
        bot.answer_callback_query(call.id, "✓ Видео выбрано")
        _show_download_options_by_chat_id(chat_id, url)
        return

    if ":" not in data:
        return

    fmt_type, quality = data.split(":", 1)
    session = user_sessions.get(chat_id)
    
    if not session or 'url' not in session:
        bot.answer_callback_query(call.id, "⚠️ Сессия устарела. Пришлите ссылку ещё раз.")
        return

    url = session['url']

    try:
        bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)
        status = "⏳ Скачиваю аудио..." if fmt_type == "audio" else f"⏳ Скачиваю {quality}p..."
        bot.edit_message_text(status, chat_id, call.message.message_id)
    except:
        pass

    bot.answer_callback_query(call.id, f"Запуск: {fmt_type} {quality}")

    try:
        if fmt_type == "audio":
            filename = _download_audio(url, chat_id)
        else:
            filename = _download_video(url, quality, chat_id)

        # чистка
        for msg_id in user_sessions.get(chat_id, {}).get('bot_messages', []):
            try:
                bot.delete_message(chat_id, msg_id)
            except:
                pass

        filesize = os.path.getsize(filename) if os.path.exists(filename) else 0
        size_str = f" ({filesize // (1024*1024)} МБ)" if filesize else ""
        bot.send_message(
            chat_id,
            f"✅ Готово!\n📁 `{os.path.basename(filename)}`{size_str}\n📂 Папка: `Download`",
            parse_mode="Markdown"
        )
        #  отчистка при успехе
        user_sessions.pop(chat_id, None)

    except (DownloadError, ExtractorError) as e:
        # ошибка формата - возврат к выбору
        error_text = str(e).lower()
        if "no suitable format" in error_text or "requested format not available" in error_text:
            bot.send_message(
                chat_id,
                f"⚠️ Формат {quality}p недоступен для этого видео.\n"
                f"🔄 Выберите другое качество:",
                reply_markup=_get_quality_markup()  # ← вынесли в отдельную функцию
            )
            bot.answer_callback_query(call.id, "⚠️ Это качество недоступно", show_alert=True)
        else:
            bot.send_message(chat_id, f"❌ Ошибка: {str(e)[:200]}")
            user_sessions.pop(chat_id, None)
            print(f"[ERROR] {type(e).__name__}: {e}")

    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка: {str(e)[:200]}")
        user_sessions.pop(chat_id, None)
        print(f"[ERROR] UNEXPECTED: {type(e).__name__}: {e}")

def _get_quality_markup():
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(
        telebot.types.InlineKeyboardButton("480p", callback_data="video:480"),
        telebot.types.InlineKeyboardButton("720p", callback_data="video:720"),
        telebot.types.InlineKeyboardButton("1080p", callback_data="video:1080")
    )
    markup.row(
        telebot.types.InlineKeyboardButton("🎧 Аудио (MP3)", callback_data="audio:mp3")
    )
    return markup
    
def _download_video(url, quality, chat_id):
    format_map = {
        "480": "best[height<=480]",
        "720": "best[height<=720]",
        "1080": "bestvideo[height<=1080]+bestaudio/best[height<=1080]"
    }
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'format': format_map.get(quality, "best"),
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)

def _download_audio(url, chat_id):
    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        base, _ = os.path.splitext(ydl.prepare_filename(info))
        return base + ".mp3"

if __name__ == "__main__":
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    print(f"[INFO] Бот запущен. Скачивание в: {DOWNLOAD_DIR}")    
    bot.polling(none_stop=True, interval=1)