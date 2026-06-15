import os
import time
import base64
import threading
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask
import yt_dlp

# ==========================================
# CONFIGURATION & SECURED LINKS (Railway Optimized)
# ==========================================
# Ab yeh direct Railway ke Variables tab se Token uthayega
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# FORCE JOIN CHANNELS (Aapke channels ka username)
CHANNEL_1 = "@plus_official01"
CHANNEL_2 = "@joinforfree110"

# Base64 Decoded Links (Mandatory Rule)
YT_LINK = base64.b64decode("aHR0cHM6Ly95b3V0dWJlLmNvbS9AYmxhY2trbm93bGVkZ2VfMTkwP3NpPTlFd2tNUEdiLWxIUnpaZHE=").decode('utf-8')
SUPPORT_LINK = base64.b64decode("aHR0cHM6Ly90Lm1lL0JMQUNLX0tub3dsZWRnZV8xOTA=").decode('utf-8')
FINAL_CAPTION = "Downloaded Successfully! Power by: @plus_official01"

# ==========================================
# FLASK KEEP-ALIVE SERVER (For Railway 24/7)
# ==========================================
app = Flask(__name__)

@app.route('/')
def index():
    return "Bot is running beautifully with Force Join on Railway!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

# ==========================================
# HELPER FUNCTIONS (Force Join Check)
# ==========================================
def is_user_subscribed(user_id):
    """Checks if the user has joined both mandatory channels."""
    try:
        status1 = bot.get_chat_member(CHANNEL_1, user_id).status
        status2 = bot.get_chat_member(CHANNEL_2, user_id).status
        
        allowed = ['member', 'administrator', 'creator']
        if status1 in allowed and status2 in allowed:
            return True
        return False
    except Exception as e:
        print(f"Force Join Check Error: {e}")
        # Agar bot channel me admin nahi hai ya koi error hai toh user ko block nahi karega crash se bachne ke liye
        return False

def send_force_join_message(chat_id):
    """Sends the premium access denied / force join layout."""
    text = (
        "❌ *Access Denied!*\n\n"
        "You must subscribe to our official channels to use this bot. "
        "Click the buttons below to join, then press **Verified 🔄**."
    )
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("📢 Join Channel 1", url="https://t.me/plus_official01"))
    markup.row(InlineKeyboardButton("📢 Join Channel 2", url="https://t.me/joinforfree110"))
    markup.row(InlineKeyboardButton("🔄 Verified / Try Again", callback_data="check_verify"))
    
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

def get_premium_welcome_markup():
    """Generates the main command layout."""
    markup = InlineKeyboardMarkup()
    btn_subscribe = InlineKeyboardButton("SUBSCRIBE CHANNEL", url=YT_LINK)
    btn_tutorials = InlineKeyboardButton("ALL TUTORIALS", url=YT_LINK)
    btn_contact = InlineKeyboardButton("CONTACT OWNER", url=SUPPORT_LINK)
    markup.add(btn_subscribe)
    markup.add(btn_tutorials)
    markup.add(btn_contact)
    return markup

# ==========================================
# TELEGRAM BOT HANDLERS
# ==========================================

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handles the /start command with Force Join Check."""
    if not is_user_subscribed(message.from_user.id):
        send_force_join_message(message.chat.id)
        return

    welcome_text = (
        "🌟 *Welcome to the Premium Downloader Bot!*\n\n"
        "I am an advanced downloader created for @BLACK_KNOWLEDGE_190. "
        "Simply send me an Instagram Reel or Facebook Video link, and I will download it for you instantly!"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=get_premium_welcome_markup(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "check_verify")
def verify_callback(call):
    """Handles the verification button click."""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    
    if is_user_subscribed(user_id):
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except Exception:
            pass
        welcome_text = (
            "✅ *Verification Successful!*\n\n"
            "Thank you for joining. I am created for @BLACK_KNOWLEDGE_190.\n"
            "Send me any Instagram Reel or Facebook Video link now!"
        )
        bot.send_message(chat_id, welcome_text, reply_markup=get_premium_welcome_markup(), parse_mode="Markdown")
    else:
        bot.answer_callback_query(call.id, "⚠️ You still haven't joined both channels!", show_alert=True)

@bot.message_handler(func=lambda message: message.text and 'http' in message.text)
def handle_video_link(message):
    """Handles incoming links with Force Join verification and UI progress."""
    if not is_user_subscribed(message.from_user.id):
        send_force_join_message(message.chat.id)
        return

    url = message.text.strip()
    if not any(domain in url for domain in ['instagram.com', 'facebook.com', 'fb.watch']):
        bot.reply_to(message, "⚠️ Please send a valid Instagram or Facebook video link.")
        return

    chat_id = message.chat.id
    status_msg = bot.reply_to(message, "⏳ Analyzing...")
    file_name = f"download_{chat_id}_{int(time.time())}.mp4"
    
    try:
        time.sleep(0.5) 
        bot.edit_message_text("🔄 Downloading (50%)...", chat_id=chat_id, message_id=status_msg.message_id)
        
        ydl_opts = {
            'outtmpl': file_name,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
            'merge_output_format': 'mp4'
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        bot.edit_message_text("🚀 Uploading (100%)...", chat_id=chat_id, message_id=status_msg.message_id)
        
        with open(file_name, 'rb') as video_file:
            bot.send_video(chat_id, video_file, caption=FINAL_CAPTION)
            
        try:
            bot.delete_message(chat_id=chat_id, message_id=status_msg.message_id)
        except Exception:
            pass

    except Exception as e:
        try:
            bot.edit_message_text(f"❌ Error during processing:\n`{str(e)}`", chat_id=chat_id, message_id=status_msg.message_id, parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id, f"❌ Error during processing:\n`{str(e)}`", parse_mode="Markdown")
        
    finally:
        if os.path.exists(file_name):
            try:
                os.remove(file_name)
            except Exception as cleanup_error:
                print(f"Failed to delete file {file_name}: {cleanup_error}")

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    print("Starting Keep-Alive Flask Server...")
    keep_alive()
    
    print("Starting Telegram Bot...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
