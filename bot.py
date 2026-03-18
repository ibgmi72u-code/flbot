

import os
import time
from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------- CONFIGURATION (replace with your own values) ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "1234567890"))   # Your Telegram user ID
CONTACT_PRIMARY = "@eatsplugus"   # e.g. @deals_florida
CONTACT_SUPPORT = "@yrfrnd_spidy"
CHANNEL_LINK = "https://t.me/flights_bills_b4u"
# ------------------------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
app = Flask(__name__)

# In‑memory storage for user IDs (for /stats and /broadcast)
user_ids = set()

# ---------- LOCATION DATA – MAJOR USA CITIES (grouped by state) ----------
# Format: {state_code: {name: "State Name", cities: {city_key: "City Name", ...}}}
STATES = {
    "AL": {"name": "Alabama", "cities": {"birmingham": "Birmingham", "huntsville": "Huntsville", "mobile": "Mobile"}},
    "AK": {"name": "Alaska", "cities": {"anchorage": "Anchorage", "fairbanks": "Fairbanks"}},
    "AZ": {"name": "Arizona", "cities": {"phoenix": "Phoenix", "tucson": "Tucson", "mesa": "Mesa", "scottsdale": "Scottsdale"}},
    "AR": {"name": "Arkansas", "cities": {"littlerock": "Little Rock", "fayetteville": "Fayetteville"}},
    "CA": {"name": "California", "cities": {"losangeles": "Los Angeles", "sandiego": "San Diego", "sf": "San Francisco", "sacramento": "Sacramento", "fresno": "Fresno", "longbeach": "Long Beach"}},
    "CO": {"name": "Colorado", "cities": {"denver": "Denver", "colosprings": "Colorado Springs", "aurora": "Aurora"}},
    "CT": {"name": "Connecticut", "cities": {"bridgeport": "Bridgeport", "newhaven": "New Haven", "hartford": "Hartford"}},
    "DE": {"name": "Delaware", "cities": {"wilmington": "Wilmington", "dover": "Dover"}},
    "FL": {"name": "Florida", "cities": {"miami": "Miami", "orlando": "Orlando", "tampa": "Tampa", "jacksonville": "Jacksonville", "tallahasse": "Tallahassee", "fortlauderdale": "Fort Lauderdale"}},
    "GA": {"name": "Georgia", "cities": {"atlanta": "Atlanta", "augusta": "Augusta", "columbus": "Columbus"}},
    "HI": {"name": "Hawaii", "cities": {"honolulu": "Honolulu"}},
    "ID": {"name": "Idaho", "cities": {"boise": "Boise"}},
    "IL": {"name": "Illinois", "cities": {"chicago": "Chicago", "aurora": "Aurora", "rockford": "Rockford"}},
    "IN": {"name": "Indiana", "cities": {"indianapolis": "Indianapolis", "fortwayne": "Fort Wayne", "evansville": "Evansville"}},
    "IA": {"name": "Iowa", "cities": {"desmoines": "Des Moines", "cedarrapids": "Cedar Rapids"}},
    "KS": {"name": "Kansas", "cities": {"wichita": "Wichita", "overlandpark": "Overland Park"}},
    "KY": {"name": "Kentucky", "cities": {"louisville": "Louisville", "lexington": "Lexington"}},
    "LA": {"name": "Louisiana", "cities": {"neworleans": "New Orleans", "batonrouge": "Baton Rouge", "shreveport": "Shreveport"}},
    "ME": {"name": "Maine", "cities": {"portland": "Portland"}},
    "MD": {"name": "Maryland", "cities": {"baltimore": "Baltimore", "rockville": "Rockville"}},
    "MA": {"name": "Massachusetts", "cities": {"boston": "Boston", "worcester": "Worcester", "springfield": "Springfield"}},
    "MI": {"name": "Michigan", "cities": {"detroit": "Detroit", "grandrapids": "Grand Rapids", "annarbor": "Ann Arbor"}},
    "MN": {"name": "Minnesota", "cities": {"minneapolis": "Minneapolis", "stpaul": "Saint Paul"}},
    "MS": {"name": "Mississippi", "cities": {"jackson": "Jackson"}},
    "MO": {"name": "Missouri", "cities": {"kansascity": "Kansas City", "stlouis": "St. Louis", "springfield": "Springfield"}},
    "MT": {"name": "Montana", "cities": {"billings": "Billings"}},
    "NE": {"name": "Nebraska", "cities": {"omaha": "Omaha", "lincoln": "Lincoln"}},
    "NV": {"name": "Nevada", "cities": {"lasvegas": "Las Vegas", "reno": "Reno"}},
    "NH": {"name": "New Hampshire", "cities": {"manchester": "Manchester"}},
    "NJ": {"name": "New Jersey", "cities": {"newark": "Newark", "jerseycity": "Jersey City", "atlanticcity": "Atlantic City", "princeton": "Princeton", "hoboken": "Hoboken"}},
    "NM": {"name": "New Mexico", "cities": {"albuquerque": "Albuquerque", "santafe": "Santa Fe"}},
    "NY": {"name": "New York", "cities": {"nyc": "New York City", "buffalo": "Buffalo", "rochester": "Rochester", "albany": "Albany"}},
    "NC": {"name": "North Carolina", "cities": {"charlotte": "Charlotte", "raleigh": "Raleigh", "greensboro": "Greensboro"}},
    "ND": {"name": "North Dakota", "cities": {"fargo": "Fargo"}},
    "OH": {"name": "Ohio", "cities": {"columbus": "Columbus", "cleveland": "Cleveland", "cincinnati": "Cincinnati", "toledo": "Toledo"}},
    "OK": {"name": "Oklahoma", "cities": {"oklahomacity": "Oklahoma City", "tulsa": "Tulsa"}},
    "OR": {"name": "Oregon", "cities": {"portland": "Portland", "salem": "Salem"}},
    "PA": {"name": "Pennsylvania", "cities": {"philadelphia": "Philadelphia", "pittsburgh": "Pittsburgh", "allentown": "Allentown"}},
    "RI": {"name": "Rhode Island", "cities": {"providence": "Providence"}},
    "SC": {"name": "South Carolina", "cities": {"columbia": "Columbia", "charleston": "Charleston"}},
    "SD": {"name": "South Dakota", "cities": {"siouxfalls": "Sioux Falls"}},
    "TN": {"name": "Tennessee", "cities": {"nashville": "Nashville", "memphis": "Memphis", "knoxville": "Knoxville"}},
    "TX": {"name": "Texas", "cities": {"houston": "Houston", "sanantonio": "San Antonio", "dallas": "Dallas", "austin": "Austin", "fortworth": "Fort Worth", "elpaso": "El Paso"}},
    "UT": {"name": "Utah", "cities": {"saltlakecity": "Salt Lake City"}},
    "VT": {"name": "Vermont", "cities": {"burlington": "Burlington"}},
    "VA": {"name": "Virginia", "cities": {"virginiabeach": "Virginia Beach", "richmond": "Richmond"}},
    "WA": {"name": "Washington", "cities": {"seattle": "Seattle", "spokane": "Spokane", "tacoma": "Tacoma"}},
    "WV": {"name": "West Virginia", "cities": {"charleston": "Charleston"}},
    "WI": {"name": "Wisconsin", "cities": {"milwaukee": "Milwaukee", "madison": "Madison"}},
    "WY": {"name": "Wyoming", "cities": {"cheyenne": "Cheyenne"}}
}

# For each city we store neighborhoods and details (customize as needed)
CITY_DETAILS = {
    # You can fill in more details for each city. For now we use a template.
    # In a real bot you might want to add specific info.
}

def get_city_details(state_code, city_key):
    """Return a description for a city, with generic neighborhoods."""
    state_name = STATES[state_code]["name"]
    city_name = STATES[state_code]["cities"][city_key]
    # Generic neighborhoods – in a real bot you could store per city
    neighborhoods = ["Downtown", "Midtown", "Suburbs", "University District"]
    details = f"📍 *{city_name}, {state_name}*\n\n"
    details += f"*Neighborhoods:* {', '.join(neighborhoods)}\n\n"
    details += f"Find **50% OFF** deals on food delivery, rideshares, rent, shopping, and entertainment in {city_name}. "
    details += "Exclusive discounts for Telegram users!"
    return details

# ---------- SERVICE DATA (generic for entire USA) ----------
SERVICES = {
    "food": {
        "title": "🍔 **FOOD DELIVERY 50% OFF**",
        "details": "• Uber Eats: First 5 orders half‑off (up to $15 each)\n"
                   "• DoorDash: 50% off delivery fees for a month\n"
                   "• Local restaurants: BOGO entrees nationwide\n"
                   "• Example: Use code USAHALF for $20 off your first order.",
    },
    "rides": {
        "title": "🚗 **RIDESHARE 50% OFF**",
        "details": "• Uber: 50% off up to 10 rides (max $10 per ride)\n"
                   "• Lyft: Half‑off airport rides in major cities\n"
                   "• Local taxis: 50% off first ride with code RIDE50\n"
                   "• Example: Airport transfer for $12 instead of $24.",
    },
    "rent": {
        "title": "🏠 **RENT 50% OFF FIRST MONTH**",
        "details": "• Apartments: 50% off first month at select buildings nationwide\n"
                   "• Student housing: Half‑off security deposit\n"
                   "• Example: Studio in downtown for $800 first month instead of $1600.",
    },
    "shopping": {
        "title": "🛍️ **SHOPPING 50% OFF**",
        "details": "• Mall outlets: 50% off at participating stores\n"
                   "• Online code SHOP50 for extra 50% off clearance\n"
                   "• Example: Nike shoes for $40 instead of $80.",
    },
    "entertainment": {
        "title": "🎬 **ENTERTAINMENT 50% OFF**",
        "details": "• Movie tickets: BOGO at AMC Theatres\n"
                   "• Concerts: 50% off select shows\n"
                   "• Attractions: Half‑off admission to zoos, museums\n"
                   "• Example: Universal Studios tickets 50% off on Wednesdays.",
    }
}

# ---------- UTILITY FUNCTIONS ----------
def build_menu_buttons():
    """Return the main menu inline keyboard (without keywords)."""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📍 States", callback_data="menu_states"),
        InlineKeyboardButton("🎯 Services", callback_data="menu_services"),
        InlineKeyboardButton("📞 Contact", callback_data="menu_contact"),
    )
    return markup

# ---------- BOT COMMAND HANDLERS ----------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_ids.add(message.from_user.id)
    welcome_text = (
        "👋 *Welcome to USA Half‑Off Bot!*\n\n"
        "I help you find **50% OFF** deals on food, rides, rent, shopping, and entertainment "
        "across the United States.\n\n"
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
    if data == "menu_states":
        # Show list of state abbreviations (two per row)
        markup = InlineKeyboardMarkup(row_width=2)
        buttons = []
        for state_code, state_info in STATES.items():
            buttons.append(InlineKeyboardButton(f"{state_code} – {state_info['name']}", callback_data=f"state_{state_code}"))
        markup.add(*buttons)
        markup.add(InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main"))
        bot.edit_message_text("📍 *Select a state:*", call.message.chat.id, call.message.message_id,
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

    elif data.startswith("state_"):
        state_code = data[6:]
        state_info = STATES.get(state_code)
        if not state_info:
            bot.answer_callback_query(call.id, "State not found.")
            return
        # Show cities in this state
        markup = InlineKeyboardMarkup(row_width=2)
        city_buttons = []
        for city_key, city_name in state_info["cities"].items():
            city_buttons.append(InlineKeyboardButton(city_name, callback_data=f"city_{state_code}_{city_key}"))
        markup.add(*city_buttons)
        markup.add(InlineKeyboardButton("🔙 Back to States", callback_data="menu_states"))
        bot.edit_message_text(f"📍 *Cities in {state_info['name']}:*", call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    elif data.startswith("city_"):
        parts = data.split("_")
        if len(parts) < 3:
            bot.answer_callback_query(call.id, "Invalid city.")
            return
        state_code = parts[1]
        city_key = parts[2]
        city_name = STATES[state_code]["cities"].get(city_key, "Unknown")
        details = get_city_details(state_code, city_key)
        markup = InlineKeyboardMarkup().add(
            InlineKeyboardButton("🔙 Back to Cities", callback_data=f"state_{state_code}"),
            InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")
        )
        bot.edit_message_text(details, call.message.chat.id, call.message.message_id, reply_markup=markup)

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
    # On Railway, the public URL is available via RAILWAY_PUBLIC_DOMAIN or can be set manually
    public_url = os.environ.get('WEBHOOK_URL')  # e.g. https://your-app.railway.app
    if not public_url:
        # Fallback: try to construct from RAILWAY_STATIC_URL
        railway_url = os.environ.get('RAILWAY_STATIC_URL')
        if railway_url:
            public_url = f"https://{railway_url}"
    if not public_url:
        print("WARNING: WEBHOOK_URL not set. Webhook not configured.")
        return
    webhook_url = f"{public_url.rstrip('/')}/webhook"
    bot.remove_webhook()
    bot.set_webhook(url=webhook_url)
    print(f"Webhook set to {webhook_url}")

if __name__ == '__main__':
    # Check if running on Railway (by presence of RAILWAY_ENVIRONMENT or similar)
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('WEBHOOK_URL'):
        set_webhook()
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    else:
        # Local testing with polling
        bot.remove_webhook()
        print("Starting polling...")
        bot.infinity_polling()
