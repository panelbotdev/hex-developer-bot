import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time

# 1. Bot Token Config
API_TOKEN = '84949765623:AAEv7b8aArzd-OGFOzc0uXvyDFdA0hFHEis'

bot = telebot.TeleBot(API_TOKEN)

# 2. Temporary Database
USER_DB = {}

def get_user_data(user_id, username="Client"):
    if user_id not in USER_DB:
        USER_DB[user_id] = {
            "balance": 0,
            "orders": 0,
            "spent": 0,
            "name": username or "Client"
        }
    return USER_DB[user_id]

# --- MENUS & KEYBOARDS ---
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🔑 6 Hours - ₹40", callback_data="plan_6h"),
        InlineKeyboardButton("🔑 12 Hours - ₹65", callback_data="plan_12h")
    )
    markup.add(
        InlineKeyboardButton("🔑 1 Day - ₹99", callback_data="plan_1d"),
        InlineKeyboardButton("🔑 7 Days - ₹220", callback_data="plan_7d")
    )
    markup.add(
        InlineKeyboardButton("👤 Profile", callback_data="view_profile"),
        InlineKeyboardButton("🛠️ Support", callback_data="view_support")
    )
    markup.add(InlineKeyboardButton("💰 Add Balance", callback_data="add_balance"))
    return markup

def numeric_keyboard():
    markup = InlineKeyboardMarkup(row_width=3)
    buttons = [InlineKeyboardButton(str(i), callback_data=f"num_{i}") for i in range(1, 10)]
    markup.add(*buttons)
    markup.add(
        InlineKeyboardButton("❌ Delete", callback_data="num_delete"),
        InlineKeyboardButton("0", callback_data="num_0"),
        InlineKeyboardButton("✅ Confirm", callback_data="num_confirm")
    )
    markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back_home"))
    return markup

# --- COMMAND HANDLERS ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    get_user_data(user_id, username)
    
    welcome_text = (
        "**HAXX BOT A/iOS**\n\n"
        "🔑 *Only Keys Available*\n"
        "⚡ *Instant Key Delivery*\n\n"
        "🛒 **SELECT YOUR PLAN:**"
    )
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown", reply_markup=main_menu())

# --- CALLBACK QUERY HANDLERS ---
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    user = get_user_data(user_id)

    if call.data.startswith("plan_"):
        plan_costs = {"plan_6h": 40, "plan_12h": 65, "plan_1d": 99, "plan_7d": 220}
        cost = plan_costs[call.data]

        if user["balance"] < cost:
            text = f"❌ **Balance kam hai!**\n\n💰 Chahiye: ₹{cost}\n💳 Aapke paas: ₹{user['balance']}"
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("➕ Add Balance", callback_data="add_balance"))
            markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back_home"))
            bot.edit_message_text(text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)
        else:
            user["balance"] -= cost
            user["orders"] += 1
            user["spent"] += cost
            bot.answer_callback_query(call.id, "✅ Purchase Successful!")
            bot.send_message(chat_id, "🔑 Here is your premium key: `SAMPLE-KEY-XXXX-YYYY`")

    elif call.data == "view_profile":
        profile_text = (
            f"👤 —— **YOUR PROFILE** —— 👤\n\n"
            f"▶️ User ID: `{user_id}`\n"
            f"▶️ Name: {user['name']}\n"
            f"▶️ Account: 🔵 Regular | ✅ Active\n\n"
            f"💰 —— **Balance** ——\n"
            f"💳 Current: ₹{user['balance']}\n\n"
            f"📊 —— **Statistics** ——\n"
            f"📦 Orders: {user['orders']}\n"
            f"💸 Spent: ₹{user['spent']}\n\n"
            f"📅 Joined: 2026-09-30"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ Back", callback_data="back_home"))
        bot.edit_message_text(profile_text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "view_support":
        support_text = (
            "🎯 **HAXX CORE — Support**\n\n"
            "👋 Our team is here to help you.\n\n"
            "We can assist with:\n"
            "— 🔑 Orders & key delivery\n"
            "— 💰 Payments & balance\n"
            "— 📦 Product questions\n\n"
            "🕒 *Typical reply time: within a few hours.*"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💬 Chat on Telegram", url="https://t.me"))
        markup.add(InlineKeyboardButton("⬅️ Back to Home", callback_data="back_home"))
        bot.edit_message_text(support_text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "add_balance":
        pay_text = "💵 **Custom Amount**\n\nMethod: 📳 UPI (ZapUPI)\n🔹 Min: ₹10 | 🔸 Max: ₹5,000\n\n📌 *Default Amount Set:* **₹200**"
        bot.edit_message_text(pay_text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=numeric_keyboard())

    elif call.data == "num_confirm":
        order_id = f"ORD{int(time.time())}"
        pay_link_text = (
            f"💳 **Pay ₹200**\n\n"
            f"📄 Order ID: `{order_id}`\n\n"
            f"1️⃣ Neeche 🟢 **Pay Now** button dabao.\n"
            f"2️⃣ Apne kisi bhi UPI app se payment complete karo.\n"
            f"3️⃣ Payment hote hi balance automatically add ho jayega.\n\n"
            f"⚠️ *Yeh payment link sirf 7 minute tak valid hai.*"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("🟢 Pay Now", url="https://zapupi.com"))
        markup.add(InlineKeyboardButton("🔴 Cancel Payment", callback_data="back_home"))
        bot.edit_message_text(pay_link_text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif call.data == "back_home":
        welcome_text = "🛒 **SELECT YOUR PLAN:**"
        bot.edit_message_text(welcome_text, chat_id, call.message.message_id, reply_markup=main_menu())

# --- START BOT ---
bot.infinity_polling()
