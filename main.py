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
# Railway Variables tab se Token load hoga
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# FORCE JOIN CHANNELS
CHANNEL_1 = "@plus_official01"
CHANNEL_2 = "@joinforfree110"

# Base64 Decoded Links (Mandatory Rule)
YT_LINK = base64.b64decode("aHR0cHM6Ly95b3V0dWJlLmNvbS9AYmxhY2trbm93bGVkZ2VfMTkwP3NpPTlFd2tNUEdiLWxIUnpaZHE=").decode('utf-8')
SUPPORT_LINK = base64.b64decode("aHR0cHM6Ly90Lm1lL0JMQUNLX0tub3dsZWRnZV8xOTA=").decode('utf-8')
FINAL_CAPTION = "⚡ *Downloaded Successfully!*\n\n🤝 *Powered by:* @plus_official01"

# ==========================================
# FLASK KEEP-ALIVE SERVER (For Railway 24/7)
# ==========================================
app = Flask(__name__)

@app.route('/')
def index():
    return "Premium Bot is running 24/7 on Railway!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

# ==========================================
# HELPER FUNCTIONS (Strict Force Join Check)
# ==========================================
def is_user_subscribed(user_id):
    """Checks if the user has strictly joined both mandatory channels."""
    allowed = ['member', 'administrator', 'creator']
    
    # Check Channel 1
    try:
        member1 = bot.get_chat_member(CHANNEL_1, user_id)
        if member1.status not in allowed:
            return False
    except Exception as e:
        print(f"[LOG] Channel 1 check failed or user not found: {e}")
        return False
        
    # Check Channel 2
    try:
        member2 = bot.get_chat_member(CHANNEL_2, user_id)
        if member2.status not in allowed:
            return False
    except Exception as e:
        print(f"[LOG] Channel 2 check failed or user not found: {e}")
        return False

    return True

def send_force_join_message(chat_id):
    """Sends a premium access denied layout with verification button."""
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
    """Handles the /start command with premium feel."""
    if not is_user_subscribed(message.from_user.id):
        send_force_join_message(message.chat.id)
        return

    welcome_text = (
        "✨ *WELCOME TO PREMIUM DOWNLOADER v2.0* ✨\n\n"
        "Hello! I am an ultra-fast media downloader configured for *@plus_official01*.\n\n"
        "📥 *Supported Platforms:*\n"
        "• Instagram Reels & Videos\n"
        "• Facebook Videos & FB Watch\n\n"
        "🚀 *How to use:* Just copy any video link and send it directly to me!"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "check_verify")
def verify_callback(call):
    """Handles the verification process safely."""
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
    """Handles links with high-fidelity progress animation."""
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
        # Step 2: Downloading Progress Layout
        time.sleep(0.4) 
        bot.edit_message_text("📥 *Downloading (50%)* \n`▓▓▓▓▓▓▓▓░░░░░░░░`", chat_id=chat_id, message_id=status_msg.message_id, parse_mode="Markdown")
        
        ydl_opts = {
            'outtmpl': file_name,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4',
            'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None # Server block se bachne ke liye
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # Step 3: Uploading Progress Layout
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
            "Reason: This specific video might be private, restricted, or the link is temporarily unavailable."
        )
        try:
            bot.edit_message_text(error_text, chat_id=chat_id, message_id=status_msg.message_id, parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id, error_text, parse_mode="Markdown")
        
    finally:
        # Mandatory Server Cleanup
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
            except Exception:
                pass

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("[SERVER] Starting Keep-Alive Flask Server...")
    keep_alive()
    
    print("[BOT] Launching Infinity Polling...")
    bot.infinity_polling(timeout=20, long_polling_timeout=10)
