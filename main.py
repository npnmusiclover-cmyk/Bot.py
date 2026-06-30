import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 0))
API_KEY = "DEMOFUCK"

bot = telebot.TeleBot(BOT_TOKEN)
USERS_FILE = 'users.txt'

# --- PREMIUM INLINE BUTTONS ---
def get_premium_markup():
    markup = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton("💠 Join PLUS OFFICIAL", url="https://t.me/plus_official01")
    btn2 = InlineKeyboardButton("💠 Join For Free 110", url="https://t.me/joinforfree110")
    markup.add(btn1, btn2)
    return markup

# --- FORCE SUB BUTTONS ---
def get_fsub_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💠 Join PLUS OFFICIAL", url="https://t.me/plus_official01"),
        InlineKeyboardButton("💠 Join For Free 110", url="https://t.me/joinforfree110"),
        InlineKeyboardButton("✅ Verify", callback_data="verify_fsub")
    )
    return markup

# --- MEMBERSHIP CHECK ---
def check_membership(user_id):
    channels = ["@plus_official01", "@joinforfree110"]
    for channel in channels:
        try:
            status = bot.get_chat_member(channel, user_id).status
            if status in ['left', 'kicked']: return False
        except: return False
    return True

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "🟣 <b>𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢 𝗕𝗢𝗧</b> 🟣\n\n"
        "Welcome to the ultimate vehicle information system.\n"
        "Kisi bhi gadi ki premium details nikalne ke liye uska number bhejiye.\n\n"
        "𝗘𝘅𝗮𝗺𝗽𝗹𝗲: <code>DL10AB1234</code>"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=get_premium_markup())

# --- VERIFY CALLBACK ---
@bot.callback_query_handler(func=lambda call: call.data == "verify_fsub")
def verify_callback(call):
    if check_membership(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Verified! Ab aap details check kar sakte hain.")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "✅ Access granted. Ab gadi ka number bhejiye.")
    else:
        bot.answer_callback_query(call.id, "❌ Pehle dono channel join karein!", show_alert=True)

# --- VEHICLE INFO FETCHING ---
@bot.message_handler(func=lambda message: True)
def get_vehicle_info(message):
    if message.text.startswith('/'): return
    
    # Force Sub Check
    if not check_membership(message.from_user.id):
        bot.reply_to(message, "⚠️ <b>Premium Access Restricted!</b>\n\nBot ka use karne ke liye, kripya niche diye gaye dono channels ko join karein aur 'Verify' par click karein.", 
                     parse_mode="HTML", reply_markup=get_fsub_markup())
        return
    
    vehicle_number = message.text.replace(" ", "").upper()
    loading_msg = bot.reply_to(message, "🟣 <i>Fetching Premium Data, please wait...</i>", parse_mode='HTML')
    
    url = f"https://anshsir-info.vercel.app/api/vehicle-info?rc={vehicle_number}&api_key={API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            if "Owner Name" in data and data.get("Owner Name"):
                clean_text = (
                    "🟣 <b>𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡</b> 🟣\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 <b>𝗢𝘄𝗻𝗲𝗿 𝗡𝗮𝗺𝗲:</b> {data.get('Owner Name', 'N/A')}\n"
                    f"🏍️ <b>𝗠𝗮𝗸𝗲𝗿/𝗠𝗼𝗱𝗲𝗹:</b> {data.get('Maker Model', 'N/A')} ({data.get('Model Name', 'N/A')})\n"
                    f"⛽ <b>𝗙𝘂𝗲𝗹 𝗧𝘆𝗽𝗲:</b> {data.get('Fuel Type', 'N/A')} ({data.get('Fuel Norms', 'N/A')})\n"
                    f"📅 <b>𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗗𝗮𝘁𝗲:</b> {data.get('Registration Date', 'N/A')}\n"
                    f"🏛️ <b>𝗥𝗧𝗢:</b> {data.get('Registered RTO', 'N/A')} ({data.get('City Name', 'N/A')})\n"
                    f"🛡️ <b>𝗜𝗻𝘀𝘂𝗿𝗮𝗻𝗰𝗲 𝗨𝗽𝘁𝗼:</b> {data.get('Insurance Upto', 'N/A')} ({data.get('Insurance Company', 'N/A')})\n"
                    f"✅ <b>𝗙𝗶𝘁𝗻𝗲𝘀𝘀 𝗨𝗽𝘁𝗼:</b> {data.get('Fitness Upto', 'N/A')}\n"
                    f"📝 <b>𝗣𝗨𝗖 𝗨𝗽𝘁𝗼:</b> {data.get('PUC Upto', 'N/A')}\n"
                    f"🏦 <b>𝗙𝗶𝗻𝗮𝗻𝗰𝗶𝗲𝗿:</b> {data.get('Financier Name', 'N/A')}\n"
                    f"📍 <b>𝗔𝗱𝗱𝗿𝗲𝘀𝘀:</b> {data.get('Address', 'N/A')}\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "⚡ <i>𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆 𝗣𝗟𝗨𝗦 𝗣𝗥𝗢</i>"
                )
                bot.edit_message_text(chat_id=message.chat.id, message_id=loading_msg.message_id, text=clean_text, parse_mode='HTML', reply_markup=get_premium_markup())
            else:
                bot.edit_message_text("❌ <b>Data not found.</b> Kripya sahi RC number bhejiye ya thodi der baad try karein.", chat_id=message.chat.id, message_id=loading_msg.message_id, parse_mode='HTML')
        else:
             bot.edit_message_text("❌ <b>Server error.</b> API limit ya technical issue.", chat_id=message.chat.id, message_id=loading_msg.message_id, parse_mode='HTML')
             
    except Exception as e:
        bot.edit_message_text("⚠️ <b>Error fetching details.</b> Try another vehicle number.", chat_id=message.chat.id, message_id=loading_msg.message_id, parse_mode='HTML')

print("🟣 Premium Bot is live...")
bot.infinity_polling()
