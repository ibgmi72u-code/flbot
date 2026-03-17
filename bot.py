import os
import threading
import time
from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

# ---------- CONFIGURATION (replace with your own values) ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "1234567890"))   # Your Telegram user ID
CONTACT_PRIMARY = "@yourprimarycontact"   # e.g. @deals_florida
CONTACT_SUPPORT = "@yoursupport"
CHANNEL_LINK = "https://t.me/your_channel"
# ------------------------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
app = Flask(__name__)

# In‑memory storage for user IDs (for /stats and /broadcast)
user_ids = set()

# ---------- DATA DICTIONARIES (customize as needed) ----------

LOCATIONS = {
    "fl_miami": {
        "name": "🌴 **MIAMI, FL**",
        "neighborhoods": ["South Beach", "Downtown", "Brickell", "Coral Gables", "Wynwood"],
        "details": "Miami offers vibrant nightlife, world‑class dining, and endless entertainment. "
                   "Get **50% OFF** on food delivery, rideshares, club entries, and more! "
                   "Example: Half‑off Uber rides to South Beach, BOGO cocktails in Brickell."
    },
    "fl_orlando": {
        "name": "🎢 **ORLANDO, FL**",
        "neighborhoods": ["Lake Buena Vista", "International Drive", "Downtown Orlando", "Winter Park"],
        "details": "Home to theme parks and family fun. Enjoy **50% OFF** on park shuttles, food delivery, "
                   "and attraction tickets. Example: Half‑off Uber to Disney Springs, 50% off pizza delivery."
    },
    "fl_tampa": {
        "name": "☀️ **TAMPA, FL**",
        "neighborhoods": ["Downtown", "Ybor City", "South Tampa", "Westshore"],
        "details": "Tampa’s waterfront and historic Ybor City come with discounts: **50% OFF** on rides, "
                   "food delivery, and even rent for the first month. Example: Half‑off Uber to Ybor."
    },
    "fl_jacksonville": {
        "name": "🏖️ **JACKSONVILLE, FL**",
        "neighborhoods": ["Downtown", "Riverside", "Beaches", "Southside"],
        "details": "Jacksonville’s sprawling beaches and urban core offer **50% OFF** on food delivery, "
                   "rideshares, and shopping. Example: Half‑off DoorDash to the Beaches."
    },
    "fl_tallahassee": {
        "name": "🏛️ **TALLAHASSEE, FL**",
        "neighborhoods": ["Downtown", "Midtown", "SouthWood", "College Town"],
        "details": "Capital city with a college vibe. Score **50% OFF** on food delivery, rides to FSU games, "
                   "and local entertainment. Example: Half‑off Uber to Doak Campbell Stadium."
    },
    "fl_fortlauderdale": {
        "name": "🛥️ **FORT LAUDERDALE, FL**",
        "neighborhoods": ["Downtown", "Las Olas", "Beach", "Victoria Park"],
        "details": "Yachting capital with great nightlife. Enjoy **50% OFF** on water taxi rides, food delivery, "
                   "and beach equipment rentals. Example: Half‑off water taxi tours."
    },
    "nj_newark": {
        "name": "🏙️ **NEWARK, NJ**",
        "neighborhoods": ["Downtown", "Ironbound", "North Newark", "Weequahic"],
        "details": "Newark’s Ironbound district is famous for cuisine. Get **50% OFF** on food delivery, "
                   "rides to/from EWR, and shopping. Example: Half‑off Uber to Prudential Center."
    },
    "nj_jerseycity": {
        "name": "🗽 **JERSEY CITY, NJ**",
        "neighborhoods": ["Downtown", "Journal Square", "The Heights", "Waterfront"],
        "details": "Just across the Hudson, Jersey City offers skyline views and **50% OFF** on PATH rides, "
                   "food delivery, and rent. Example: Half‑off first month’s rent in luxury buildings."
    },
    "nj_atlanticcity": {
        "name": "🎰 **ATLANTIC CITY, NJ**",
        "neighborhoods": ["Boardwalk", "Marina District", "Downtown", "Chelsea"],
        "details": "Famous casinos and boardwalk. Take **50% OFF** on casino shuttles, food delivery, "
                   "and show tickets. Example: Half‑off Uber to the Borgata."
    },
    "nj_princeton": {
        "name": "📚 **PRINCETON, NJ**",
        "neighborhoods": ["Downtown", "University", "Princeton Junction", "Kingston"],
        "details": "Ivy League charm with discounts: **50% OFF** on food delivery, rides, and local bookstores. "
                   "Example: Half‑off Uber to Princeton campus."
    },
    "nj_hoboken": {
        "name": "🍕 **HOBOKEN, NJ**",
        "neighborhoods": ["Downtown", "Uptown", "Mile Square", "Waterfront"],
        "details": "Hoboken’s nightlife and pizza scene come with **50% OFF** on food delivery, rides, "
                   "and bar tabs. Example: Half‑off Uber to Maxwell’s Tavern."
    }
}

SERVICES = {
    "food": {
        "title": "🍔 **FOOD DELIVERY 50% OFF**",
        "details": "• Uber Eats: First 5 orders half‑off (up to $15 each)\n"
                   "• DoorDash: 50% off delivery fees for a month\n"
                   "• Local restaurants: BOGO entrees in Miami, Orlando, Newark\n"
                   "• Example: Use code FLHALF for $20 off your first order.",
        "keywords": ["food delivery half off", "restaurant discounts", "Uber Eats promo", "DoorDash coupon"]
    },
    "rides": {
        "title": "🚗 **RIDESHARE 50% OFF**",
        "details": "• Uber: 50% off up to 10 rides (max $10 per ride)\n"
                   "• Lyft: Half‑off airport rides in FL & NJ\n"
                   "• Local taxis: 50% off first ride with code NJRIDE\n"
                   "• Example: Miami to South Beach for $5 instead of $10.",
        "keywords": ["Uber half off", "Lyft discount", "rideshare deals", "airport rides half price"]
    },
    "rent": {
        "title": "🏠 **RENT 50% OFF FIRST MONTH**",
        "details": "• Apartments in Jersey City: 50% off first month at select buildings\n"
                   "• Miami luxury condos: Half‑off security deposit\n"
                   "• Orlando student housing: 50% off first month with student ID\n"
                   "• Example: Studio in Newark for $800 first month instead of $1600.",
        "keywords": ["apartment deals", "first month half off", "rent discount", "student housing"]
    },
    "shopping": {
        "title": "🛍️ **SHOPPING 50% OFF**",
        "details": "• Mall outlets: 50% off at participating stores in Sawgrass Mills (FL)\n"
                   "• Jersey Gardens (NJ): Half‑off coupon book\n"
                   "• Online code SHOP50 for extra 50% off clearance\n"
                   "• Example: Nike shoes for $40 instead of $80.",
        "keywords": ["shopping deals", "outlet mall discounts", "clothing half off", "electronics sale"]
    },
    "entertainment": {
        "title": "🎬 **ENTERTAINMENT 50% OFF**",
        "details": "• Movie tickets: BOGO at AMC Theatres (FL & NJ)\n"
                   "• Concerts: 50% off select shows at Hard Rock Live\n"
                   "• Attractions: Half‑off admission to Miami Zoo, Adventure Aquarium\n"
                   "• Example: Universal Studios tickets 50% off on Wednesdays.",
        "keywords": ["movie deals", "concert discounts", "theme park half off", "attraction coupons"]
    }
}

SEO_KEYWORDS = {
    "primary": ["Florida half off", "New Jersey 50% off", "Florida deals", "NJ discounts"],
    "secondary": [
        "Miami half price", "Orlando discounts", "Newark deals", "Jersey City 50% off",
        "Tampa services half off", "Fort Lauderdale offers", "Atlantic City promotions",
        "Jacksonville half off", "Tallahassee discounts", "Princeton deals"
    ],
    "location_based": [
        "Miami half off services", "Orlando 50% off", "Tampa half price", "Jacksonville deals",
        "Newark discounts", "Jersey City half off", "Atlantic City promotions", "Princeton deals"
    ],
    "service_based": [
        "Food delivery half off Florida", "Rideshare discounts New Jersey", "Rent half off Florida",
        "Dining deals NJ", "Shopping 50% off Florida", "Entertainment discounts NJ"
    ]
}

# ---------- UTILITY FUNCTIONS ----------
def build_menu_buttons():
    """Return the main menu inline keyboard."""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📍 Locations", callback_data="menu_locations"),
        InlineKeyboardButton("🎯 Services", callback_data="menu_services"),
        InlineKeyboardButton("📞 Contact", callback_data="menu_contact"),
        InlineKeyboardButton("🔑 Keywords", callback_data="menu_keywords")
    )
    return markup

# ---------- BOT COMMAND HANDLERS ----------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_ids.add(message.from_user.id)
    welcome_text = (
        "👋 *Welcome to Florida & New Jersey Half‑Off Bot!*\n\n"
        "I help you find **50% OFF** deals on food, rides, rent, shopping, and entertainment "
        "across Florida and New Jersey.\n\n"
        "Choose an option below to get started 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=build_menu_buttons())

@bot.message_handler(commands=['stats'])
def stats_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ You are not authorized to use this command.")
        return
    bot.reply_to(message, f"📊 *Total users seen:* {len(user_ids)}")

@bot.message_handler(commands=['broadcast'])
def broadcast_command(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ Unauthorized.")
        return
    msg = bot.reply_to(message, "📢 Send the message you want to broadcast to all users:")
    bot.register_next_step_handler(msg, send_broadcast)

def send_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return
    text = message.text
    success = 0
    fail = 0
    for uid in user_ids:
        try:
            bot.send_message(uid, f"📢 *Broadcast:*\n\n{text}")
            success += 1
        except Exception:
            fail += 1
    bot.reply_to(message, f"✅ Broadcast sent to {success} users.\n❌ Failed: {fail}")

# ---------- CALLBACK QUERY HANDLERS ----------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data

    # Main menu
    if data == "menu_locations":
        markup = InlineKeyboardMarkup(row_width=2)
        # Create a list of buttons for each location (using keys)
        loc_buttons = []
        for loc_key, loc_info in LOCATIONS.items():
            loc_buttons.append(InlineKeyboardButton(loc_info["name"], callback_data=f"loc_{loc_key}"))
        markup.add(*loc_buttons)
        markup.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main"))
        bot.edit_message_text("📍 *Select a location:*", call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    elif data == "menu_services":
        markup = InlineKeyboardMarkup(row_width=2)
        serv_buttons = []
        for serv_key, serv_info in SERVICES.items():
            serv_buttons.append(InlineKeyboardButton(serv_info["title"], callback_data=f"serv_{serv_key}"))
        markup.add(*serv_buttons)
        markup.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main"))
        bot.edit_message_text("🎯 *Choose a service category:*", call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    elif data == "menu_contact":
        contact_text = (
            "📞 *Contact Information*\n\n"
            f"Primary: {CONTACT_PRIMARY}\n"
            f"Support: {CONTACT_SUPPORT}\n"
            f"Channel: {CHANNEL_LINK}\n\n"
            "Feel free to reach out for partnership or questions!"
        )
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main"))
        bot.edit_message_text(contact_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data == "menu_keywords":
        keywords_text = (
            "🔑 *SEO Keywords we target:*\n\n"
            "*Primary:*\n" + ", ".join(SEO_KEYWORDS["primary"]) + "\n\n"
            "*Secondary:*\n" + ", ".join(SEO_KEYWORDS["secondary"]) + "\n\n"
            "*Location‑based:*\n" + ", ".join(SEO_KEYWORDS["location_based"]) + "\n\n"
            "*Service‑based:*\n" + ", ".join(SEO_KEYWORDS["service_based"])
        )
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main"))
        bot.edit_message_text(keywords_text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data.startswith("loc_"):
        loc_key = data[4:]
        loc = LOCATIONS.get(loc_key)
        if not loc:
            bot.answer_callback_query(call.id, "Location not found.")
            return
        text = f"{loc['name']}\n\n*Neighborhoods:* {', '.join(loc['neighborhoods'])}\n\n{loc['details']}"
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🔙 Back to Locations", callback_data="menu_locations"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data.startswith("serv_"):
        serv_key = data[5:]
        serv = SERVICES.get(serv_key)
        if not serv:
            bot.answer_callback_query(call.id, "Service not found.")
            return
        text = f"{serv['title']}\n\n{serv['details']}"
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🔙 Back to Services", callback_data="menu_services"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")
        )
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data == "back_to_main":
        bot.edit_message_text(
            "👋 *Main Menu* – choose an option:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=build_menu_buttons()
        )

    # Always answer callback to remove loading state
    bot.answer_callback_query(call.id)

# ---------- DEFAULT HANDLER ----------
@bot.message_handler(func=lambda message: True)
def default_handler(message):
    bot.reply_to(message, "I didn't understand that. Please use the buttons below.", reply_markup=build_menu_buttons())

# ---------- FLASK WEBHOOK ROUTES ----------
@app.route('/')
def home():
    return "Bot is running!"

@app.route('/webhook', methods=['POST'])
def webhook():
    json_str = request.get_data(as_text=True)
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return jsonify({"status": "ok"}), 200

# ---------- SET WEBHOOK (run once on startup) ----------
def set_webhook():
    time.sleep(1)  # Give time for Flask to start if needed
    webhook_url = os.environ.get('RENDER_EXTERNAL_URL', 'https://your-app.onrender.com') + '/webhook'
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    print(f"Webhook set to {webhook_url}")

if __name__ == '__main__':
    # In production (Render) we set the webhook once, then run Flask.
    # For local testing, you can use polling instead.
    if os.environ.get('RENDER'):  # Running on Render
        set_webhook()
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    else:
        # Local testing with polling (remove webhook)
        bot.remove_webhook()
        print("Starting polling...")
        # Run Flask in a separate thread if needed, or just use polling.
        # For simplicity, we'll just start polling and ignore Flask locally.
        # To test webhook locally, use ngrok and set WEBHOOK_URL env.
        bot.infinity_polling()
