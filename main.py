import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os

# Railway Environment Variables se tokens uthayenge
BOT_TOKEN = os.environ.get('BOT_TOKEN') 
ADMIN_ID = int(os.environ.get('ADMIN_ID', 0)) # Apna Telegram ID dalein Railway variables mein
API_KEY = "DEMOFUCK"

bot = telebot.TeleBot(BOT_TOKEN)
USERS_FILE = 'users.txt'

# --- PREMIUM INLINE BUTTONS ---
def get_premium_markup():
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("💠 Join PLUS OFFICIAL", url="https://t.me/plus_official01")
    btn2 = InlineKeyboardButton("💠 Join For Free 110", url="https://t.me/joinforfree110")
    markup.add(btn1)
    markup.add(btn2)
    return markup

# --- USER DATABASE FOR BROADCAST ---
def save_user(user_id):
    users = get_all_users()
    if str(user_id) not in users:
        with open(USERS_FILE, 'a') as f:
            f.write(f"{user_id}\n")

def get_all_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, 'r') as f:
        return [line.strip() for line in f.readlines()]

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    save_user(message.chat.id)
    welcome_text = (
        "🟣 **𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢 𝗕𝗢𝗧** 🟣\n\n"
        "Welcome to the ultimate vehicle information system.\n"
        "Kisi bhi gadi ki premium details nikalne ke liye uska number bhejiye.\n\n"
        "𝗘𝘅𝗮𝗺𝗽𝗹𝗲: `DL10AB1234`"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='Markdown', reply_markup=get_premium_markup())

# --- ADMIN BROADCAST COMMAND ---
@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Aap admin nahi hain.")
        return
    
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        bot.reply_to(message, "⚠️ Format: `/broadcast <aapka message>`")
        return

    users = get_all_users()
    success = 0
    bot.reply_to(message, "⏳ Broadcast shuru ho raha hai...")
    
    for user in users:
        try:
            bot.send_message(chat_id=user, text=f"📢 **Admin Message:**\n\n{text}", parse_mode='Markdown')
            success += 1
        except:
            pass # Agar user ne bot block kar diya ho
            
    bot.reply_to(message, f"✅ Broadcast Complete!\nTotal users: {len(users)}\nSent to: {success}")

# --- VEHICLE INFO FETCHING ---
@bot.message_handler(func=lambda message: True)
def get_vehicle_info(message):
    if message.text.startswith('/'): return
    
    save_user(message.chat.id)
    vehicle_number = message.text.replace(" ", "").upper()
    
    loading_msg = bot.reply_to(message, "🟣 *Fetching Premium Data, please wait...*", parse_mode='Markdown')
    
    url = f"https://anshsir-info.vercel.app/api/vehicle-info?rc={vehicle_number}&api_key={API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Agar data exist karta hai
            if "Owner Name" in data:
                clean_text = (
                    "🟣 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡 🟣\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 **𝗢𝘄𝗻𝗲𝗿 𝗡𝗮𝗺𝗲:** {data.get('Owner Name', 'N/A')}\n"
                    f"🏍️ **𝗠𝗮𝗸𝗲𝗿/𝗠𝗼𝗱𝗲𝗹:** {data.get('Maker Model', 'N/A')} ({data.get('Model Name', 'N/A')})\n"
                    f"⛽ **𝗙𝘂𝗲𝗹 𝗧𝘆𝗽𝗲:** {data.get('Fuel Type', 'N/A')} ({data.get('Fuel Norms', 'N/A')})\n"
                    f"📅 **𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗗𝗮𝘁𝗲:** {data.get('Registration Date', 'N/A')}\n"
                    f"🏛️ **𝗥𝗧𝗢:** {data.get('Registered RTO', 'N/A')} ({data.get('City Name', 'N/A')})\n"
                    f"🛡️ **𝗜𝗻𝘀𝘂𝗿𝗮𝗻𝗰𝗲 𝗨𝗽𝘁𝗼:** {data.get('Insurance Upto', 'N/A')} ({data.get('Insurance Company', 'N/A')})\n"
                    f"✅ **𝗙𝗶𝘁𝗻𝗲𝘀𝘀 𝗨𝗽𝘁𝗼:** {data.get('Fitness Upto', 'N/A')}\n"
                    f"📝 **𝗣𝗨𝗖 𝗨𝗽𝘁𝗼:** {data.get('PUC Upto', 'N/A')}\n"
                    f"🏦 **𝗙𝗶𝗻𝗮𝗻𝗰𝗶𝗲𝗿:** {data.get('Financier Name', 'N/A')}\n"
                    f"📍 **𝗔𝗱𝗱𝗿𝗲𝘀𝘀:** {data.get('Address', 'N/A')}\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "⚡ *𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆 𝗣𝗟𝗨𝗦 𝗣𝗥𝗢*"
                )
                bot.edit_message_text(chat_id=message.chat.id, message_id=loading_msg.message_id, text=clean_text, parse_mode='Markdown', reply_markup=get_premium_markup())
            else:
                bot.edit_message_text(chat_id=message.chat.id, message_id=loading_msg.message_id, text="❌ Data not found ya phir API expire ho chuki hai.")
        else:
             bot.edit_message_text(chat_id=message.chat.id, message_id=loading_msg.message_id, text="❌ Server error. Kripya thodi der baad try karein.")
             
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=loading_msg.message_id, text="⚠️ *Error fetching details.*", parse_mode='Markdown')

print("🟣 Premium Bot is live...")
bot.infinity_polling()
