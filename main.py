import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os
import time
import threading

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
ADMIN_ID = int(os.environ.get('ADMIN_ID', 0))
RC_API_KEY = "DEMOFUCK"

bot = telebot.TeleBot(BOT_TOKEN)

# Maintenance States
MAINTENANCE = {"all": False, "rc": False, "number": False}

# --- HELPERS ---
def get_premium_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💠 Join PLUS OFFICIAL", url="https://t.me/plus_official01"))
    markup.add(InlineKeyboardButton("💠 Join For Free 110", url="https://t.me/joinforfree110"))
    return markup

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
        text = "🟣 <b>PREMIUM INFO BOT</b> 🟣\n\nGadi ka number ya Mobile number bhejiye."
        bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=get_premium_markup())

# --- MAIN LOGIC ---
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.text.startswith('/'): return
    
    if MAINTENANCE['all']:
        bot.reply_to(message, "🚧 <b>BOT UNDER MAINTENANCE</b> 🚧\n\nHum system update kar rahe hain. Kripya thodi der baad wapas aayein. 🙏", parse_mode='HTML')
        return

    query = message.text.replace(" ", "")
    loading = bot.reply_to(message, "⏳ <i>Fetching...</i>", parse_mode='HTML')
    
    # MOBILE INFO
    if query.isdigit() and len(query) == 10:
        if MAINTENANCE['number']:
            bot.edit_message_text("❌ <b>Mobile Service Maintenance mein hai.</b>\nMaafi chahte hain! 🙏", message.chat.id, loading.message_id, parse_mode='HTML')
            return
            
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
        else: res = "🔍 <b>Oops! Data Not Found</b>\n\nIs mobile number ki details nahi mil saki. Kripya check karein. 🙏"
    
    # RC INFO
    else:
        if MAINTENANCE['rc']:
            bot.edit_message_text("❌ <b>RC Service Maintenance mein hai.</b>\nMaafi chahte hain! ✨", message.chat.id, loading.message_id, parse_mode='HTML')
            return
            
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
        else: res = "🔍 <b>Vehicle Details Not Found</b>\n\nIs gadi ka record nahi mila. Kripya sahi number check karein. ✨"

    msg = bot.edit_message_text(res, message.chat.id, loading.message_id, parse_mode='HTML', reply_markup=get_premium_markup())
    threading.Thread(target=auto_delete, args=(msg,)).start()

print("🟣 Premium Bot is live...")
bot.infinity_polling()
