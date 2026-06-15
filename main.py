import os
import time
import base64
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import yt_dlp

# ==========================================
# CONFIGURATION & SECURED LINKS
# ==========================================
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

CHANNEL_1 = "@plus_official01"
CHANNEL_2 = "@joinforfree110"

YT_LINK = base64.b64decode("aHR0cHM6Ly95b3V0dWJlLmNvbS9AYmxhY2trbm93bGVkZ2VfMTkwP3NpPTlFd2tNUEdiLWxIUnpaZHE=").decode('utf-8')
SUPPORT_LINK = base64.b64decode("aHR0cHM6Ly90Lm1lL0JMQUNLX0tub3dsZWRnZV8xOTA=").decode('utf-8')
FINAL_CAPTION = "⚡ *Downloaded Successfully!*\n\n🤝 *Powered by:* @plus_official01"

# ==========================================
# FLASK KEEP-ALIVE SERVER (For Railway 24/7)
# ==========================================
app = Flask(__name__)

@app.route('/')
def index():
    return "Premium Bot is Running Seamlessly!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

# ==========================================
# HELPER FUNCTIONS
# ==========================================
def is_user_subscribed(user_id):
    allowed = ['member', 'administrator', 'creator']
    try:
        member1 = bot.get_chat_member(CHANNEL_1, user_id)
        if member1.status not in allowed:
            return False
    except Exception:
        return False
        
    try:
        member2 = bot.get_chat_member(CHANNEL_2, user_id)
        if member2.status not in allowed:
            return False
    except Exception:
        return False

    return True

def send_force_join_message(chat_id):
    text = (
        "🔒 *PREMIUM ACCESS LOCKED*\n\n"
        "Hey! To use this high-speed downloader, you must join our official updates channels first.\n\n"
        "👇 *Join both channels below:* "
    )
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📢 Plus Official", url="https://t.me/plus_official01"))
    markup.row(InlineKeyboardButton("📢 Free Join", url="https://t.me/joinforfree110"))
    markup.row(InlineKeyboardButton("🔄 Verify Access / Refresh", callback_data="check_verify"))
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

# ==========================================
# TELEGRAM BOT HANDLERS
# ==========================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if not is_user_subscribed(message.from_user.id):
        send_force_join_message(message.chat.id)
        return

    welcome_text = (
        "✨ *WELCOME TO PREMIUM DOWNLOADER v2.5* ✨\n\n"
        "Hello! I am an ultra-fast media downloader configured for *@plus_official01*.\n\n"
        "📥 *Supported Platforms:*\n"
        "• Instagram Reels & Videos\n"
        "• Facebook Videos & FB Watch\n\n"
        "🚀 *How to use:* Just copy any video link and send it directly to me!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "check_verify")
def verify_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if is_user_subscribed(user_id):
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except Exception:
            pass
            
        welcome_text = (
            "✅ *ACCESS GRANTED!*\n\n"
            "Thank you for verifying. Your premium access has been activated.\n\n"
            "💬 *Send me any Instagram Reel or Facebook Video link now!*"
        )
        bot.send_message(chat_id, welcome_text, parse_mode="Markdown")
    else:
        bot.answer_callback_query(call.id, "⚠️ Access Denied! Please join both channels first.", show_alert=True)

@bot.message_handler(func=lambda message: message.text and 'http' in message.text)
def handle_video_link(message):
    if not is_user_subscribed(message.from_user.id):
        send_force_join_message(message.chat.id)
        return

    url = message.text.strip()
    if not any(domain in url for domain in ['instagram.com', 'facebook.com', 'fb.watch']):
        bot.reply_to(message, "⚠️ *Invalid Link!* Please send a valid Instagram or Facebook link.", parse_mode="Markdown")
        return

    chat_id = message.chat.id
    status_msg = bot.reply_to(message, "⚡ *Analyzing URL... Please wait.*", parse_mode="Markdown")
    file_name = f"premium_{chat_id}_{int(time.time())}.mp4"
    
    try:
        time.sleep(0.4) 
        bot.edit_message_text("📥 *Downloading (50%)* \n`▓▓▓▓▓▓▓▓░░░░░░░░`", chat_id=chat_id, message_id=status_msg.message_id, parse_mode="Markdown")
        
        # ADVANCED BYPASS OPTIONS FOR INSTAGRAM/FACEBOOK BLOCK
        ydl_opts = {
            'outtmpl': file_name,
            # Sabse best format nikalega, agar fail hua toh directly pure mp4 download karega
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
            # Fake Mobile Browser Headers taaki Instagram block na kare
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        bot.edit_message_text("🚀 *Uploading to Telegram (100%)* \n`▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓`", chat_id=chat_id, message_id=status_msg.message_id, parse_mode="Markdown")
        
        with open(file_name, 'rb') as video_file:
            bot.send_video(chat_id, video_file, caption=FINAL_CAPTION, parse_mode="Markdown")
            
        try:
            bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
        except Exception:
            pass

    except Exception as e:
        print(f"[ERROR] Download failed: {e}")
        error_text = (
            "❌ *Download Failed!*\n\n"
            "Instagram/Facebook server heavily loaded or video is private. Please try again after 1-2 minutes."
        )
        try:
            bot.edit_message_text(error_text, chat_id=chat_id, message_id=status_msg.message_id, parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id, error_text, parse_mode="Markdown")
        
    finally:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
            except Exception:
                pass

if __name__ == "__main__":
    print("[SERVER] Starting Keep-Alive Flask Server...")
    keep_alive()
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
