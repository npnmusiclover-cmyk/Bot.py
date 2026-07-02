import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os
import time
import threading

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

# --- ADMIN PANEL ---
@bot.message_handler(commands=['admin'])
def admin_panel(message):
    if message.from_user.id != ADMIN_ID: return
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(f"🚨 Bot Maintenance: {'ON' if MAINTENANCE['all'] else 'OFF'}", callback_data="toggle_all"),
        InlineKeyboardButton(f"🚗 RC Service: {'OFF' if MAINTENANCE['rc'] else 'ON'}", callback_data="toggle_rc"),
        InlineKeyboardButton(f"📱 Mobile Service: {'OFF' if MAINTENANCE['number'] else 'ON'}", callback_data="toggle_number")
    )
    bot.reply_to(message, "⚙️ <b>ADMIN CONTROL PANEL</b>", reply_markup=markup, parse_mode='HTML')

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
    if message.from_user.id == ADMIN_ID:
        bot.send_message(message.chat.id, "👑 <b>ADMIN DASHBOARD</b>\nUse /admin for settings.", parse_mode='HTML')
    else:
        if is_member(message.from_user.id):
            text = (
                "🟣 <b>PREMIUM INFO BOT</b> 🟣\n\n"
                "Gadi ka number check karne ke liye: <code>/rc MP09XX0000</code>\n"
                "Mobile number check karne ke liye: <code>/num 9876543210</code>"
            )
            bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_premium_markup())
        else:
            bot.send_message(message.chat.id, "⚠️ <b>ACCESS DENIED</b>\n\nBot use karne ke liye pehle niche diye gaye channels join karein.", parse_mode='HTML', reply_markup=get_join_markup())

# --- MOBILE LOGIC (/num) ---
@bot.message_handler(commands=['num'])
def handle_num(message):
    # Persistent Channel Check (Left verification)
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
    # Persistent Channel Check (Left verification)
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

print("🟣 Premium Bot is live...")
bot.infinity_polling()
