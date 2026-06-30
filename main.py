import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os

# Railway Environment Variables
BOT_TOKEN = os.environ.get('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE') 
ADMIN_ID = int(os.environ.get('ADMIN_ID', 0))
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

# --- FORCE SUB BUTTONS ---
def get_fsub_markup():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💠 Join PLUS OFFICIAL", url="https://t.me/plus_official01"),
        InlineKeyboardButton("💠 Join For Free 110", url="https://t.me/joinforfree110"),
        InlineKeyboardButton("✅ Verify", callback_data="verify_fsub")
    )
    return markup

# --- CHECK MEMBERSHIP FUNCTION ---
def check_membership(user_id):
    channels = ["@plus_official01", "@joinforfree110"]
    for channel in channels:
        try:
            # Bot MUST be an admin in these channels for this to work perfectly
            status = bot.get_chat_member(channel, user_id).status
            if status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            print(f"Error checking channel {channel}: {e}")
            return False
    return True

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
        "🟣 <b>𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢 𝗕𝗢𝗧</b> 🟣\n\n"
        "Welcome to the ultimate vehicle information system.\n"
        "Kisi bhi gadi ki premium details nikalne ke liye uska number bhejiye.\n\n"
        "𝗘𝘅𝗮𝗺𝗽𝗹𝗲: <code>DL10AB1234</code>"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode='HTML', reply_markup=get_premium_markup())

# --- ADMIN BROADCAST COMMAND ---
@bot.message_handler(commands=['broadcast'])
def broadcast_message(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "❌ Aap admin nahi hain.")
        return
    
    text = message.text.replace("/broadcast", "").strip()
    if not text:
        bot.reply_to(message, "⚠️ Format: <code>/broadcast &lt;aapka message&gt;</code>", parse_mode='HTML')
        return

    users = get_all_users()
    success = 0
    bot.reply_to(message, "⏳ Broadcast shuru ho raha hai...")
    
    for user in users:
        try:
            bot.send_message(chat_id=user, text=f"📢 <b>Admin Message:</b>\n\n{text}", parse_mode='HTML')
            success += 1
        except:
            pass 
            
    bot.reply_to(message, f"✅ Broadcast Complete!\nTotal users: {len(users)}\nSent to: {success}")

# --- CALLBACK HANDLER FOR VERIFY BUTTON ---
@bot.callback_query_handler(func=lambda call: call.data == "verify_fsub")
def verify_callback(call):
    if check_membership(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Verification Successful! Ab aap bot use kar sakte hain.")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, "🟣 Please send any vehicle number to get premium details.")
    else:
        bot.answer_callback_query(call.id, "❌ Aapne abhi tak dono channels join nahi kiye hain! Pehle join karein.", show_alert=True)

# --- VEHICLE INFO FETCHING ---
@bot.message_handler(func=lambda message: True)
def get_vehicle_info(message):
    if message.text.startswith('/'): return
    
    user_id = message.from_user.id
    save_user(user_id)

    # --- FORCE SUB CHECK BEFORE GIVING DETAILS ---
    if not check_membership(user_id):
        fsub_text = (
            "⚠️ <b>Premium Access Restricted!</b>\n\n"
            "Bot ka use karne ke liye, kripya niche diye gaye dono official channels ko join karein.\n"
            "Join karne ke baad <b>'✅ Verify'</b> button par click karein."
        )
        bot.reply_to(message, fsub_text, parse_mode="HTML", reply_markup=get_fsub_markup())
        return
    
    vehicle_number = message.text.replace(" ", "").upper()
    loading_msg = bot.reply_to(message, "🟣 <i>Fetching Premium Data, please wait...</i>", parse_mode='HTML')
    
    url = f"https://anshsir-info.vercel.app/api/vehicle-info?rc={vehicle_number}&api_key={API_KEY}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            
            # Agar data exist karta hai aur error message na ho
            if "Owner Name" in data and data.get("Owner Name") != "":
                
                # HTML parse_mode used here so asterisks in names don't break the bot
                clean_text = (
                    "🟣 <b>𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗩𝗘𝗛𝗜𝗖𝗟𝗘 𝗜𝗡𝗙𝗢𝗥𝗠𝗔𝗧𝗜𝗢𝗡</b> 🟣\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    f"👤 <b>𝗢𝘄𝗻𝗲𝗿 𝗡𝗮𝗺𝗲:</b> {data.get('Owner Name', 'N/A')}\n"
                    f"🏍️ <b>𝗠𝗮𝗸𝗲𝗿/𝗠𝗼𝗱𝗲𝗹:</b> {data.get('Maker Model', 'N/A')} ({data.get('Model Name', 'N/A')})\n"
                    f"⛽ <b>𝗙𝘂𝗲𝗹 𝗧𝘆𝗽𝗲:</b> {data.get('Fuel Type', 'N/A')} ({data.get('Fuel Norms', 'N/A')})\n"
                    f"📅 <b>𝗥𝗲𝗴𝗶𝘀𝘁𝗿𝗮𝘁𝗶𝗼𝗻 𝗗𝗮𝘁𝗲:</b> {data.get('Registration Date', 'N/A')}\n"
                    f"🏛️ <b>𝗥𝗧𝗢:</b> {data.get('Registered RTO', 'N/A')} ({data.get('City Name', 'N/A')})\n"
                    f"🛡️ <b>𝗜𝗻𝘀𝘂𝗿𝗮𝗻𝗰𝗲 𝗨𝗽𝘁𝗼:</b> {data.get('Insurance Expiry', 'N/A')} ({data.get('Insurance Company', 'N/A')})\n"
                    f"✅ <b>𝗙𝗶𝘁𝗻𝗲𝘀𝘀 𝗨𝗽𝘁𝗼:</b> {data.get('Fitness Upto', 'N/A')}\n"
                    f"📝 <b>𝗣𝗨𝗖 𝗨𝗽𝘁𝗼:</b> {data.get('PUC Upto', 'N/A')}\n"
                    f"🏦 <b>𝗙𝗶𝗻𝗮𝗻𝗰𝗶𝗲𝗿:</b> {data.get('Financier Name', 'N/A')}\n"
                    f"📍 <b>𝗔𝗱𝗱𝗿𝗲𝘀𝘀:</b> {data.get('Address', 'N/A')}\n"
                    "━━━━━━━━━━━━━━━━━━━━━━\n"
                    "⚡ <i>𝗣𝗼𝘄𝗲𝗿𝗲𝗱 𝗕𝘆 𝗣𝗟𝗨𝗦 𝗣𝗥𝗢</i>"
                )
                bot.edit_message_text(chat_id=message.chat.id, message_id=loading_msg.message_id, text=clean_text, parse_mode='HTML', reply_markup=get_premium_markup())
            else:
                # Agar vehicle ki details nahi milti API mein
                not_found_text = (
                    "❌ <b>Details Not Found!</b>\n\n"
                    "Is vehicle number ki details hamare database ya API mein available nahi hain.\n"
                    "Kripya apna RC number check karein ya koi dusra vehicle number try karein.\n\n"
                    "💡 <i>Example: DL10AB1234</i>"
                )
                bot.edit_message_text(chat_id=message.chat.id, message_id=loading_msg.message_id, text=not_found_text, parse_mode='HTML')
        else:
             bot.edit_message_text(chat_id=message.chat.id, message_id=loading_msg.message_id, text="❌ <b>Server error.</b> Kripya thodi der baad try karein.", parse_mode='HTML')
             
    except Exception as e:
        print(f"Error: {e}") # Isse console mein error ka exact reason dikhega
        bot.edit_message_text(chat_id=message.chat.id, message_id=loading_msg.message_id, text="⚠️ <b>Error fetching details.</b>\nNetwork issue ya API expire ho chuki hai.", parse_mode='HTML')

print("🟣 Premium Bot is live...")
bot.infinity_polling()
