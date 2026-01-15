import os
import requests
import telebot
from telebot import types

# --- CONFIGURATION ---
TOKEN = "8163888185:AAHqjYUWUJJDUC5kcZlXEjsgSyIvD8aK4xA"
API_URL = "https://yt-data-api.onrender.com/api/fetch"

# Initialize Bot
bot = telebot.TeleBot(TOKEN)

# --- PROFESSIONAL KEYBOARD ---
def get_start_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn1 = types.InlineKeyboardButton("📺 Sample Link", url="https://youtu.be/97XtKuwWBkQ?si=0Fqf5b0_3vcWfeR2")
    btn2 = types.InlineKeyboardButton("😎 Developer", url="https://t.me/dev2dex")
    markup.add(btn1, btn2)
    return markup

# --- BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def start_command(message):
    user_name = message.from_user.first_name
    welcome_text = (
        f"🔱 *Greetings, {user_name}!*\n\n"
        "The *YouTube Advanced Metadata Extractor* is now fully operational.\n\n"
        "Send a valid YouTube URL to receive a professional breakdown of video analytics, "
        "channel insights, and high-definition assets.\n\n"
        "📍 *Status:* Professional Mode Active 💀"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_start_keyboard())

@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def handle_extraction(message):
    chat_id = message.chat.id
    processing_msg = bot.send_message(chat_id, "⚙️ *Initializing Extraction...*", parse_mode="Markdown")
    
    try:
        # Requesting data from your API
        response = requests.get(f"{API_URL}?url={message.text.strip()}", timeout=30)
        res = response.json()

        if res.get("success"):
            d = res["data"]
            v = d["video_metadata"]
            c = d["channel_details"]
            st = d["status"]

            caption = (
                f"🔱 *YOUTUBE METADATA REPORT*\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎬 *VIDEO INFO*\n"
                f"• *Title:* `{v['title']}`\n"
                f"• *Category:* {v['category']}\n"
                f"• *Views:* {v['views']}\n"
                f"• *Published:* {v['uploaded_at']}\n\n"
                f"👤 *CHANNEL INFO*\n"
                f"• *Name:* {c['name']}\n"
                f"• *Subscribers:* {c['subscribers']}\n"
                f"• *Total Views:* {c['total_views']}\n\n"
                f"⚖️ *STATUS*\n"
                f"• *Copyright Free:* {st['copyright_free']}\n"
                f"• *Age Restricted:* {st['age_restricted']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"😎 *Developer:* @dev2dex"
            )

            # High-Res Image Logic
            thumb = d["thumbnails"]["max_res"] if d["thumbnails"]["max_res"] != "N/A" else d["thumbnails"]["standard"]
            
            # Direct Image Injection
            bot.send_photo(chat_id, thumb, caption=caption, parse_mode="Markdown")
            bot.delete_message(chat_id, processing_msg.message_id)

        else:
            bot.edit_message_text("❌ *Error:* Link is invalid or private.", chat_id, processing_msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(f"⚠️ *System Error:* Contact @dev2dex", chat_id, processing_msg.message_id, parse_mode="Markdown")

# --- EXECUTION ---
if __name__ == "__main__":
    print("🔥 Bot is Starting...")
    # Infinity polling without Flask to avoid Port binding issues on Render
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
