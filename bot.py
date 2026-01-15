import os
import requests
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# --- CONFIGURATION ---
TOKEN = "8163888185:AAHqjYUWUJJDUC5kcZlXEjsgSyIvD8aK4xA"
API_URL = "https://yt-data-api.onrender.com/api/fetch"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# --- WEB SERVER FOR RENDER (KEEP ALIVE) ---
@app.route('/')
def status():
    return "🔱 YT Data Master Bot is Online & Operational."

def run():
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

# --- PROFESSIONAL UI COMPONENTS ---
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
        "Welcome to the *YouTube Advanced Metadata Extractor*.\n\n"
        "I am a professional-grade tool designed to provide deep insights into YouTube content, "
        "including high-resolution media, channel statistics, and compliance data.\n\n"
        "📍 *Instruction:* Simply send a valid YouTube URL to begin extraction."
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=get_start_keyboard())

@bot.message_handler(func=lambda m: "youtube.com" in m.text or "youtu.be" in m.text)
def handle_extraction(message):
    chat_id = message.chat.id
    processing_msg = bot.reply_to(message, "⚙️ *Initializing Extraction... Please wait.*", parse_mode="Markdown")
    
    try:
        # Requesting data from your Hosted API
        response = requests.get(f"{API_URL}?url={message.text}", timeout=25)
        res = response.json()

        if res.get("success"):
            d = res["data"]
            v = d["video_metadata"]
            c = d["channel_details"]
            st = d["status"]

            # --- PROFESSIONAL DATA TABLE ---
            caption = (
                f"🔱 *YOUTUBE ADVANCED METADATA*\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"🎬 *VIDEO INFORMATION*\n"
                f"• *Title:* `{v['title']}`\n"
                f"• *Category:* {v['category']}\n"
                f"• *Duration:* {v['duration']}\n"
                f"• *Views:* {v['views']}\n"
                f"• *Likes:* {v['likes']}\n"
                f"• *Published:* {v['uploaded_at']}\n\n"
                f"👤 *CHANNEL INSIGHTS*\n"
                f"• *Name:* {c['name']}\n"
                f"• *Subscribers:* {c['subscribers']}\n"
                f"• *Videos:* {c['total_videos']}\n"
                f"• *Lifetime Views:* {c['total_views']}\n\n"
                f"⚖️ *COMPLIANCE & STATUS*\n"
                f"• *Copyright Free:* {st['copyright_free']}\n"
                f"• *Age Restricted:* {st['age_restricted']}\n"
                f"• *Privacy:* {st['privacy']}\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n"
                f"😎 *Developer:* @dev2dex"
            )

            # --- DIRECT IMAGE INJECTION (MEDIA GROUP) ---
            media_group = []
            
            # 1. High-Res Thumbnail
            thumb = d["thumbnails"]["max_res"] if d["thumbnails"]["max_res"] != "N/A" else d["thumbnails"]["standard"]
            if thumb != "N/A":
                media_group.append(types.InputMediaPhoto(thumb, caption=caption, parse_mode="Markdown"))
            
            # 2. Channel Profile Picture (Logo)
            if c["logo"] != "N/A":
                media_group.append(types.InputMediaPhoto(c["logo"]))

            # Sending the Album
            if media_group:
                bot.send_media_group(chat_id, media_group)
            else:
                bot.send_message(chat_id, caption, parse_mode="Markdown")

            bot.delete_message(chat_id, processing_msg.message_id)

        else:
            bot.edit_message_text("❌ *Error:* Failed to retrieve data. The URL may be private or invalid.", chat_id, processing_msg.message_id, parse_mode="Markdown")

    except Exception as e:
        bot.edit_message_text(f"⚠️ *System Error:* `{str(e)}`", chat_id, processing_msg.message_id, parse_mode="Markdown")

# --- EXECUTION ---
if __name__ == "__main__":
    # Start Flask Server in Background
    Thread(target=run).start()
    
    print("🔥 YT Data Master Bot is starting...")
    bot.infinity_polling()
