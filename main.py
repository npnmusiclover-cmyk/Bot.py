import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os
import time
import threading
import json

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 8351165824))
RC_API_KEY = "DEMOFUCK"

bot = telebot.TeleBot(BOT_TOKEN)

# Channels Config
CHANNEL_1 = "@plus_official01"
CHANNEL_2 = "@joinforfree110"

# Maintenance States
MAINTENANCE = {"all": False, "rc": False, "number": False}

# Database File for Users
USERS_FILE = "users.json"

# --- USER DATABASE HELPERS ---
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            try: return json.load(f)
            except: return {}
    return {}

def save_user(user_id, name, username):
    users = load_users()
    uid_str = str(user_id)
    if uid_str not in users:
        users[uid_str] = {"name": name, "username": username}
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
        return True # Returns True if it's a new user
    return False

# --- HELPERS ---
def is_member(user_id):
    try:
        for ch in [CHANNEL_1, CHANNEL_2]:
            status = bot.get_chat_member(ch, user_id).status
            if status in ['left', 'kicked']: return False
        return True
    except:
        return False

def get_join_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💠 Join PLUS OFFICIAL", url="https://t.me/plus_official01"))
    markup.add(InlineKeyboardButton("💠 Join For Free 110", url="https://t.me/joinforfree110"))
    markup.add(InlineKeyboardButton("✅ VERIFY NOW", callback_data="verify_join"))
    return markup

def get_premium_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💠 Join PLUS OFFICIAL", url="https://t.me/plus_official01"))
    markup.add(InlineKeyboardButton("💠 Join For Free 110", url="https://t.me/joinforfree110"))
    return markup

def send_long_message(chat_id, text):
    if len(text) > 4096:
        for i in range(0, len(text), 4096):
            bot.send_message(chat_id, text[i:i+4096], parse_mode='HTML')
        return None
    else:
        return bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=get_premium_markup())

def auto_delete(message):
    time.sleep(30)
    try: bot.delete_message(message.chat.id, message.message_id)
    except: pass

# --- ADMIN PANEL & COMMANDS ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    users = load_users()
    total_users = len(users)
    
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"🚨 Bot Maintenance: {'ON' if MAINTENANCE['all'] else 'OFF'}", callback_data="toggle_all"),
        InlineKeyboardButton(f"🚗 RC Service: {'OFF' if MAINTENANCE['rc'] else 'ON'}", callback_data="toggle_rc"),
        InlineKeyboardButton(f"📱 Mobile Service: {'OFF' if MAINTENANCE['number'] else 'ON'}", callback_data="toggle_number"),
        InlineKeyboardButton(f"👥 Total Users: {total_users}", callback_data="ignore")
    )
    
    text = (
        "⚙️ <b>ADMIN CONTROL PANEL</b>\n\n"
        "<b>Admin Commands:</b>\n"
        "🔹 /admin - Open this panel\n"
        "🔹 /userlist - Get full list of users\n"
        "🔹 /searchuser [Name/ID] - Find specific user\n\n"
        "📢 <b>Broadcast Trick:</b> Aap bot me direct koi bhi message, photo ya video send karenge toh wo automatic sabhi users ko broadcast ho jayega (bina kisi command ke)."
    )
    bot.reply_to(message, text, reply_markup=markup, parse_mode='HTML')

@bot.message_handler(commands=['userlist'])
def show_userlist(message):
    if message.from_user.id != ADMIN_ID: return
    users = load_users()
    if not users:
        bot.reply_to(message, "❌ Abhi tak koi user nahi hai.")
        return
    
    text = "👥 <b>ALL USERS LIST</b>\n\n"
    for uid, data in users.items():
        text += f"👤 <b>{data['name']}</b> (@{data['username']}) - <code>{uid}</code>\n"
    
    send_long_message(message.chat.id, text)

@bot.message_handler(commands=['searchuser'])
def search_user(message):
    if message.from_user.id != ADMIN_ID: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Kripya name ya ID dalein.\nExample: <code>/searchuser Pawan</code>", parse_mode='HTML')
        return
    
    query = parts[1].lower()
    users = load_users()
    results = ""
    for uid, data in users.items():
        if query in uid or query in data['name'].lower() or query in data['username'].lower():
            results += f"👤 <b>{data['name']}</b> (@{data['username']}) - <code>{uid}</code>\n"
    
    if results:
        send_long_message(message.chat.id, f"🔍 <b>SEARCH RESULTS</b>\n\n{results}")
    else:
        bot.reply_to(message, "❌ Koi user match nahi hua.")

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_join(call):
    if is_member(call.from_user.id):
        bot.answer_callback_query(call.id, "✅ Verified Successfully!")
        bot.send_message(call.message.chat.id, "🎉 <b>Verification Successful!</b>\nAb aap details search kar sakte hain.", parse_mode='HTML', reply_markup=get_premium_markup())
    else:
        bot.answer_callback_query(call.id, "❌ Pehle dono channels join karo!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_"))
def toggle_service(call):
    if call.data == "toggle_all": MAINTENANCE['all'] = not MAINTENANCE['all']
    elif call.data == "toggle_rc": MAINTENANCE['rc'] = not MAINTENANCE['rc']
    elif call.data == "toggle_number": MAINTENANCE['number'] = not MAINTENANCE['number']
    bot.answer_callback_query(call.id, "✅ Status Updated!")

# --- START COMMAND ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username or "No Username"
    
    # Save user and notify admin if new
    is_new = save_user(user_id, name, username)
    if is_new:
        try: bot.send_message(ADMIN_ID, f"🔔 <b>NEW USER ALERT</b>\n\n👤 <b>Name:</b> {name}\n🔗 <b>Username:</b> @{username}\n🆔 <b>ID:</b> <code>{user_id}</code>", parse_mode='HTML')
        except: pass

    if user_id == ADMIN_ID:
        bot.send_message(message.chat.id, "👑 <b>ADMIN DASHBOARD</b>\nUse /admin for settings and features.", parse_mode='HTML')
    else:
        if is_member(user_id):
            text = (
                "🌟 <b>WELCOME TO PREMIUM INFO BOT</b> 🌟\n\n"
                "Aapka swagat hai! Yahan aap kisi bhi gadi ya mobile number ki details nikal sakte hain.\n\n"
                "🛠 <b>BOT COMMANDS:</b>\n"
                "🔹 /start - Bot ko restart karne ke liye\n"
                "🔹 /rc <code>[Gadi Number]</code> - RC details nikalne ke liye\n"
                "🔹 /num <code>[Mobile Number]</code> - Mobile details nikalne ke liye\n\n"
                "📌 <i>Example:</i>\n"
                "👉 <code>/rc MP09XX0000</code>\n"
                "👉 <code>/num 9876543210</code>"
            )
            bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_premium_markup())
        else:
            bot.send_message(message.chat.id, "⚠️ <b>ACCESS DENIED</b>\n\nBot use karne ke liye pehle niche diye gaye channels join karein.", parse_mode='HTML', reply_markup=get_join_markup())

# --- MOBILE LOGIC (/num) ---
@bot.message_handler(commands=['num'])
def handle_num(message):
    if not is_member(message.from_user.id):
        bot.reply_to(message, "⚠️ <b>Access Denied!</b>\nAapne channel leave kar diya hai. Kripya firse join karke Verify karein.", reply_markup=get_join_markup(), parse_mode='HTML')
        return
        
    if MAINTENANCE['all'] or MAINTENANCE['number']:
        bot.reply_to(message, "🚧 <b>BOT/SERVICE UNDER MAINTENANCE</b> 🚧\n\nHum system update kar rahe hain. Kripya thodi der baad wapas aayein. 🙏", parse_mode='HTML')
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Kripya mobile number dalein.\nUdaharan: <code>/num 9876543210</code>", parse_mode='HTML')
        return
        
    query = parts[1].replace(" ", "")
    
    if not (query.isdigit() and len(query) == 10):
        bot.reply_to(message, "❌ Invalid Mobile Number! Kripya 10 anko ka number dalein.", parse_mode='HTML')
        return

    loading = bot.reply_to(message, "⏳ <i>Fetching...</i>", parse_mode='HTML')
    
    try:
        data = requests.get(f"https://sher-osint-india-num-info.vercel.app/api?number={query}").json()
        if data.get("success"):
            d = data["number_detail"]
            res = (f"🟣 <b>MOBILE INFO</b> 🟣\n\n"
                   f"👤 <b>Name:</b> {d.get('name')}\n"
                   f"👨‍👧‍👦 <b>Father:</b> {d.get('father_name')}\n"
                   f"📞 <b>Phone:</b> {query}\n"
                   f"📧 <b>Email:</b> {d.get('email')}\n"
                   f"📡 <b>Operator:</b> {d.get('operator')}\n"
                   f"📍 <b>Circle:</b> {d.get('circle')}\n"
                   f"🏘️ <b>Village/City:</b> {d.get('village_city')}\n"
                   f"🗺️ <b>District:</b> {d.get('district')}\n"
                   f"📍 <b>State:</b> {d.get('state')}\n"
                   f"📍 <b>Landmark:</b> {d.get('landmark')}\n"
                   f"📮 <b>Pincode:</b> {d.get('pincode')}\n"
                   f"🏠 <b>Address:</b> {d.get('full_address')}")
        else: 
            res = "🔍 <b>Oops! Data Not Found</b>\n\nIs mobile number ki details nahi mil saki. Kripya check karein. 🙏"
    except:
        res = "❌ API Error! Baad me try karein."

    try: bot.delete_message(message.chat.id, loading.message_id)
    except: pass

    msg = send_long_message(message.chat.id, res)
    if msg: 
        threading.Thread(target=auto_delete, args=(msg,)).start()

# --- RC LOGIC (/rc) ---
@bot.message_handler(commands=['rc'])
def handle_rc(message):
    if not is_member(message.from_user.id):
        bot.reply_to(message, "⚠️ <b>Access Denied!</b>\nAapne channel leave kar diya hai. Kripya firse join karke Verify karein.", reply_markup=get_join_markup(), parse_mode='HTML')
        return
        
    if MAINTENANCE['all'] or MAINTENANCE['rc']:
        bot.reply_to(message, "🚧 <b>BOT/SERVICE UNDER MAINTENANCE</b> 🚧\n\nHum system update kar rahe hain. Kripya thodi der baad wapas aayein. 🙏", parse_mode='HTML')
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Kripya gadi number dalein.\nUdaharan: <code>/rc MP09XX0000</code>", parse_mode='HTML')
        return
        
    query = parts[1].replace(" ", "")
    loading = bot.reply_to(message, "⏳ <i>Fetching...</i>", parse_mode='HTML')
    
    try:
        data = requests.get(f"https://anshsir-info.vercel.app/api/vehicle-info?rc={query}&api_key={RC_API_KEY}").json()
        if "Owner Name" in data:
            res = (f"🟣 <b>VEHICLE INFO</b> 🟣\n\n"
                   f"👤 <b>Owner:</b> {data.get('Owner Name')}\n"
                   f"👔 <b>Father:</b> {data.get('Father\'s Name')}\n"
                   f"📞 <b>Phone:</b> {data.get('Phone')}\n"
                   f"🏍️ <b>Maker:</b> {data.get('Maker Model')}\n"
                   f"🏗️ <b>Model:</b> {data.get('Model Name')}\n"
                   f"⛽ <b>Fuel:</b> {data.get('Fuel Type')} ({data.get('Fuel Norms')})\n"
                   f"📅 <b>Reg Date:</b> {data.get('Registration Date')}\n"
                   f"🏛️ <b>RTO:</b> {data.get('Registered RTO')} ({data.get('City Name')})\n"
                   f"🛡️ <b>Insurance:</b> {data.get('Insurance Upto')} ({data.get('Insurance Company')})\n"
                   f"✅ <b>Fitness:</b> {data.get('Fitness Upto')}\n"
                   f"📝 <b>PUC:</b> {data.get('PUC Upto')}\n"
                   f"🏦 <b>Financier:</b> {data.get('Financier Name')}\n"
                   f"📍 <b>Address:</b> {data.get('Address')}\n"
                   f"🔢 <b>Serial:</b> {data.get('Owner Serial No')}\n"
                   f"📂 <b>Class:</b> {data.get('Vehicle Class')}")
        else: 
            res = "🔍 <b>Vehicle Details Not Found</b>\n\nIs gadi ka record nahi mila. Kripya sahi number check karein. ✨"
    except:
        res = "❌ API Error! Baad me try karein."

    try: bot.delete_message(message.chat.id, loading.message_id)
    except: pass

    msg = send_long_message(message.chat.id, res)
    if msg: 
        threading.Thread(target=auto_delete, args=(msg,)).start()

# --- ADMIN BROADCAST & UNKNOWN COMMAND CATCHER ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'animation', 'sticker'])
def catch_all(message):
    # Agar message Admin se aaya hai
    if message.from_user.id == ADMIN_ID:
        if message.text and message.text.startswith('/'):
            return # Ignore wrong commands sent by admin
            
        users = load_users()
        success = 0
        failed = 0
        
        msg = bot.reply_to(message, "⏳ <i>Broadcast started...</i>", parse_mode='HTML')
        
        for uid_str in users.keys():
            try:
                bot.copy_message(chat_id=int(uid_str), from_chat_id=message.chat.id, message_id=message.message_id)
                success += 1
                time.sleep(0.05) # Anti-Spam Limit
            except:
                failed += 1
                
        bot.edit_message_text(f"✅ <b>Broadcast Completed!</b>\n\n📨 <b>Sent:</b> {success}\n❌ <b>Failed:</b> {failed}", message.chat.id, msg.message_id, parse_mode='HTML')
    
    # Agar message normal user ne send kiya (jo ki command nahi hai)
    else:
        bot.reply_to(message, "❌ Invalid Input!\n\nKripya commands ka use karein:\n👉 <code>/rc [Gadi Number]</code>\n👉 <code>/num [Mobile Number]</code>", parse_mode='HTML')

print("🟣 Premium Bot is live...")
bot.infinity_polling()
