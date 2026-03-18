
import os
import time
from flask import Flask, request, jsonify
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------- CONFIGURATION (set these in Railway environment variables) ----------
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "1234567890"))          # Your Telegram user ID
CONTACT_PRIMARY = os.environ.get("CONTACT_PRIMARY", "@primary")   # e.g. @deals_us
CONTACT_SUPPORT = os.environ.get("CONTACT_SUPPORT", "@support")
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://t.me/your_channel")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://your-app.railway.app")  # Your Railway app URL
# --------------------------------------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")
app = Flask(__name__)

# In‑memory user storage (for /stats and /broadcast)
user_ids = set()

# ---------- LOCATIONS – Major U.S. Cities (expandable) ----------
# Format: "city_state" : { "name": display name, "neighborhoods": list, "details": description }
LOCATIONS = {
    "ny_newyork": {
        "name": "🗽 **NEW YORK, NY**",
        "neighborhoods": ["Manhattan", "Brooklyn", "Queens", "Bronx", "Staten Island"],
        "details": "The city that never sleeps – get **50% OFF** on food delivery, rideshares, Broadway tickets, and more! Example: Half‑off Uber to Times Square."
    },
    "ca_losangeles": {
        "name": "🌴 **LOS ANGELES, CA**",
        "neighborhoods": ["Downtown", "Hollywood", "Santa Monica", "Venice", "Beverly Hills"],
        "details": "Entertainment capital with discounts on studio tours, food delivery, and car rentals. Example: 50% off first rental with Turo."
    },
    "il_chicago": {
        "name": "🏙️ **CHICAGO, IL**",
        "neighborhoods": ["Loop", "Lincoln Park", "Wicker Park", "Hyde Park", "Lakeview"],
        "details": "Windy City deals: half‑off deep dish pizza delivery, 50% off Navy Pier attractions, and discounted rides."
    },
    "tx_houston": {
        "name": "🚀 **HOUSTON, TX**",
        "neighborhoods": ["Downtown", "Uptown", "Midtown", "The Heights", "Sugar Land"],
        "details": "Space City savings: 50% off NASA tours, half‑price food delivery, and discounted hotel stays."
    },
    "az_phoenix": {
        "name": "☀️ **PHOENIX, AZ**",
        "neighborhoods": ["Downtown", "Scottsdale", "Tempe", "Mesa", "Glendale"],
        "details": "Desert deals: half‑off golf rounds, 50% off rental cars, and discounted spring training tickets."
    },
    "pa_philadelphia": {
        "name": "🔔 **PHILADELPHIA, PA**",
        "neighborhoods": ["Center City", "Fishtown", "University City", "Northern Liberties"],
        "details": "Liberty Bell discounts: 50% off cheesesteak delivery, half‑price museum entries, and more."
    },
    "tx_sanantonio": {
        "name": "🌮 **SAN ANTONIO, TX**",
        "neighborhoods": ["Downtown", "Alamo Heights", "Southtown", "The Pearl"],
        "details": "River Walk savings: half‑off boat tours, 50% off Tex‑Mex delivery, and discounted hotel stays."
    },
    "ca_sandiego": {
        "name": "🏖️ **SAN DIEGO, CA**",
        "neighborhoods": ["Downtown", "La Jolla", "Pacific Beach", "Mission Valley"],
        "details": "America's Finest City deals: 50% off zoo tickets, half‑price fish tacos delivery, and discounted surf rentals."
    },
    "tx_dallas": {
        "name": "🤠 **DALLAS, TX**",
        "neighborhoods": ["Uptown", "Deep Ellum", "Bishop Arts", "Oak Lawn"],
        "details": "Big D bargains: half‑off BBQ delivery, 50% off Dallas Museum of Art entry, and discounted rides."
    },
    "ca_sanjose": {
        "name": "💻 **SAN JOSE, CA**",
        "neighborhoods": ["Downtown", "Willow Glen", "Santana Row", "Evergreen"],
        "details": "Silicon Valley savings: 50% off tech museum tickets, half‑price food delivery, and discounted ride shares."
    },
    "tx_austin": {
        "name": "🎸 **AUSTIN, TX**",
        "neighborhoods": ["Downtown", "South Congress", "East Austin", "Zilker"],
        "details": "Live Music Capital deals: half‑off concert tickets, 50% off BBQ delivery, and discounted bike rentals."
    },
    "fl_jacksonville": {
        "name": "🏖️ **JACKSONVILLE, FL**",
        "neighborhoods": ["Downtown", "Riverside", "Beaches", "Southside"],
        "details": "Jax deals: 50% off food delivery, half‑price kayak rentals, and discounted rides to the beaches."
    },
    "tx_fortworth": {
        "name": "🐄 **FORT WORTH, TX**",
        "neighborhoods": ["Downtown", "Stockyards", "Cultural District", "West 7th"],
        "details": "Cowtown discounts: 50% off rodeo tickets, half‑price BBQ delivery, and discounted western wear."
    },
    "oh_columbus": {
        "name": "🏛️ **COLUMBUS, OH**",
        "neighborhoods": ["Downtown", "Short North", "German Village", "Clintonville"],
        "details": "Ohio capital deals: 50% off zoo tickets, half‑price food delivery, and discounted OSU game shuttles."
    },
    "nc_charlotte": {
        "name": "🏎️ **CHARLOTTE, NC**",
        "neighborhoods": ["Uptown", "SouthPark", "NoDa", "Plaza Midwood"],
        "details": "Queen City savings: 50% off NASCAR Hall of Fame, half‑price food delivery, and discounted rides."
    },
    "ca_sanfrancisco": {
        "name": "🌉 **SAN FRANCISCO, CA**",
        "neighborhoods": ["Downtown", "Mission", "Fisherman's Wharf", "Haight-Ashbury"],
        "details": "Bay Area bargains: 50% off Alcatraz tours, half‑price sourdough delivery, and discounted cable car rides."
    },
    "in_indianapolis": {
        "name": "🏁 **INDIANAPOLIS, IN**",
        "neighborhoods": ["Downtown", "Broad Ripple", "Fountain Square", "Mass Ave"],
        "details": "Indy 500 deals: 50% off race tickets, half‑price tenderloin delivery, and discounted rentals."
    },
    "wa_seattle": {
        "name": "☕ **SEATTLE, WA**",
        "neighborhoods": ["Downtown", "Capitol Hill", "Ballard", "Fremont"],
        "details": "Emerald City savings: 50% off coffee tours, half‑price seafood delivery, and discounted ferry rides."
    },
    "co_denver": {
        "name": "🏔️ **DENVER, CO**",
        "neighborhoods": ["Downtown", "LoDo", "Capitol Hill", "Cherry Creek"],
        "details": "Mile High deals: 50% off ski rentals, half‑price green chili delivery, and discounted concert tickets."
    },
    "dc_washington": {
        "name": "🏛️ **WASHINGTON, DC**",
        "neighborhoods": ["Downtown", "Georgetown", "Capitol Hill", "Dupont Circle"],
        "details": "Nation's capital discounts: 50% off museum passes, half‑price food delivery, and discounted bike shares."
    },
    "ma_boston": {
        "name": "🍀 **BOSTON, MA**",
        "neighborhoods": ["Back Bay", "Beacon Hill", "North End", "South Boston"],
        "details": "Beantown bargains: 50% off Freedom Trail tours, half‑price clam chowder delivery, and discounted ferry rides."
    },
    "tn_nashville": {
        "name": "🎸 **NASHVILLE, TN**",
        "neighborhoods": ["Downtown", "Midtown", "East Nashville", "The Gulch"],
        "details": "Music City savings: 50% off honky‑tonk covers, half‑price hot chicken delivery, and discounted pedal taverns."
    },
    "mi_detroit": {
        "name": "🚗 **DETROIT, MI**",
        "neighborhoods": ["Downtown", "Midtown", "Corktown", "Greektown"],
        "details": "Motor City deals: 50% off car rentals, half‑price coney dogs delivery, and discounted museum entries."
    },
    "ok_oklahomacity": {
        "name": "🤠 **OKLAHOMA CITY, OK**",
        "neighborhoods": ["Downtown", "Bricktown", "Plaza District", "Paseo"],
        "details": "OKC bargains: 50% off cowboys museum, half‑price BBQ delivery, and discounted river cruises."
    },
    "or_portland": {
        "name": "🌲 **PORTLAND, OR**",
        "neighborhoods": ["Downtown", "Pearl District", "Alberta", "Hawthorne"],
        "details": "Rose City savings: 50% off food cart delivery, half‑price bike rentals, and discounted brewery tours."
    },
    "nv_lasvegas": {
        "name": "🎰 **LAS VEGAS, NV**",
        "neighborhoods": ["The Strip", "Downtown", "Summerlin", "Henderson"],
        "details": "Sin City deals: 50% off show tickets, half‑price buffet delivery, and discounted limo rides."
    },
    "tn_memphis": {
        "name": "🎸 **MEMPHIS, TN**",
        "neighborhoods": ["Downtown", "Midtown", "Cooper-Young", "South Main"],
        "details": "Blues City bargains: 50% off Graceland tours, half‑price BBQ delivery, and discounted riverboat cruises."
    },
    "ky_louisville": {
        "name": "🏇 **LOUISVILLE, KY**",
        "neighborhoods": ["Downtown", "Highlands", "NuLu", "Old Louisville"],
        "details": "Derby City savings: 50% off Churchill Downs tours, half‑price bourbon delivery, and discounted hot browns."
    },
    "md_baltimore": {
        "name": "🦀 **BALTIMORE, MD**",
        "neighborhoods": ["Inner Harbor", "Fells Point", "Canton", "Federal Hill"],
        "details": "Charm City deals: 50% off aquarium tickets, half‑price crab delivery, and discounted water taxis."
    },
    "wi_milwaukee": {
        "name": "🍺 **MILWAUKEE, WI**",
        "neighborhoods": ["Downtown", "Third Ward", "East Side", "Bay View"],
        "details": "Brew City bargains: 50% off brewery tours, half‑price brat delivery, and discounted lake cruises."
    },
    "nm_albuquerque": {
        "name": "🌶️ **ALBUQUERQUE, NM**",
        "neighborhoods": ["Old Town", "Downtown", "Nob Hill", "North Valley"],
        "details": "Duke City savings: 50% off balloon fiesta tickets, half‑price green chile delivery, and discounted pueblo tours."
    },
    "az_tucson": {
        "name": "🏜️ **TUCSON, AZ**",
        "neighborhoods": ["Downtown", "Fourth Avenue", "Oro Valley", "Sahuarita"],
        "details": "Old Pueblo deals: 50% off desert museum, half‑price Sonoran hot dog delivery, and discounted bike rentals."
    },
    "ca_fresno": {
        "name": "🍇 **FRESNO, CA**",
        "neighborhoods": ["Downtown", "Tower District", "Clovis", "Fig Garden"],
        "details": "Central Valley savings: 50% off fruit picking tours, half‑price food delivery, and discounted Yosemite shuttles."
    },
    "ca_sacramento": {
        "name": "🏛️ **SACRAMENTO, CA**",
        "neighborhoods": ["Downtown", "Midtown", "East Sacramento", "Land Park"],
        "details": "Capital city bargains: 50% off railroad museum, half‑price farm‑to‑fork delivery, and discounted river cruises."
    },
    "ks_kansascity": {
        "name": "⛲ **KANSAS CITY, MO/KS**",
        "neighborhoods": ["Downtown", "Crossroads", "Plaza", "Westport"],
        "details": "KC deals: 50% off BBQ delivery, half‑price jazz shows, and discounted fountains tours."
    },
    "ca_longbeach": {
        "name": "🛳️ **LONG BEACH, CA**",
        "neighborhoods": ["Downtown", "Belmont Shore", "Naples", "Bixby Knolls"],
        "details": "Aquatic city savings: 50% off aquarium tickets, half‑price water taxi rides, and discounted cruise parking."
    },
    "ga_atlanta": {
        "name": "🍑 **ATLANTA, GA**",
        "neighborhoods": ["Downtown", "Midtown", "Buckhead", "Old Fourth Ward"],
        "details": "Hotlanta bargains: 50% off aquarium tickets, half‑price peach delivery, and discounted MARTA passes."
    },
    "fl_miami": {
        "name": "🌴 **MIAMI, FL**",
        "neighborhoods": ["South Beach", "Downtown", "Brickell", "Coral Gables"],
        "details": "Magic City deals: 50% off boat rentals, half‑price cafecito delivery, and discounted club entries."
    }
    # Add more cities as needed (follow the same pattern)
}

# ---------- SERVICES – Expanded Categories ----------
SERVICES = {
    "food": {
        "title": "🍔 *FOOD DELIVERY 50% OFF*",
        "details": "• Uber Eats: First 5 orders half‑off (up to $15 each)\n"
                   "• DoorDash: 50% off delivery fees for a month\n"
                   "• Local restaurants: BOGO entrees in most cities\n"
                   "• Example: Use code USAHALF for $20 off your first order.",
        "keywords": ["food delivery half off", "restaurant discounts", "Uber Eats promo", "DoorDash coupon"]
    },
    "rides": {
        "title": "🚗 *RIDESHARE 50% OFF*",
        "details": "• Uber: 50% off up to 10 rides (max $10 per ride)\n"
                   "• Lyft: Half‑off airport rides nationwide\n"
                   "• Local taxis: 50% off first ride with code RIDE50\n"
                   "• Example: JFK to Manhattan for $15 instead of $30.",
        "keywords": ["Uber half off", "Lyft discount", "rideshare deals", "airport rides half price"]
    },
    "rentals": {
        "title": "🚙 *CAR RENTALS 50% OFF*",
        "details": "• Turo: 50% off first rental (up to $50)\n"
                   "• Enterprise: Half‑off weekend rentals\n"
                   "• Local agencies: 50% off with student ID\n"
                   "• Example: Convertible in Miami for $35/day instead of $70.",
        "keywords": ["car rental discount", "Turo promo", "rental car half off", "weekend rental deals"]
    },
    "flights": {
        "title": "✈️ *FLIGHTS 50% OFF*",
        "details": "• Select domestic routes: 50% off base fare\n"
                   "• Companion tickets: BOGO on major airlines\n"
                   "• Last‑minute deals: Half‑off flights within 48 hours\n"
                   "• Example: NYC to LAX for $99 one‑way.",
        "keywords": ["cheap flights", "airfare half off", "flight deals", "BOGO airline tickets"]
    },
    "hotels": {
        "title": "🏨 *HOTELS 50% OFF*",
        "details": "• First booking on Hotels.com: 50% off\n"
                   "• Luxury stays: Half‑off suites in participating hotels\n"
                   "• Extended stay: 50% off weekly rates\n"
                   "• Example: 4‑star Chicago hotel for $80/night instead of $160.",
        "keywords": ["hotel discounts", "lodging half off", "hotel deals", "cheap accommodation"]
    },
    "cardbills": {
        "title": "💳 *CREDIT CARD BILLS 50% OFF*",
        "details": "• Balance transfer offers: 0% APR + 50% off transfer fees\n"
                   "• Cashback doubled on select categories\n"
                   "• Example: Get $50 statement credit after $100 spend.",
        "keywords": ["credit card deals", "bill payment discount", "statement credit", "balance transfer offer"]
    },
    "hospital": {
        "title": "🏥 *MEDICAL SERVICES 50% OFF*",
        "details": "• Telehealth visits: Half‑off first consultation\n"
                   "• Prescription discounts: 50% off at partner pharmacies\n"
                   "• Dental checkups: BOGO cleaning\n"
                   "• Example: Virtual doctor visit for $25 instead of $50.",
        "keywords": ["medical discount", "telehealth half off", "prescription coupon", "dental deals"]
    },
    "school": {
        "title": "🎓 *EDUCATION 50% OFF*",
        "details": "• Online courses: 50% off first month\n"
                   "• Test prep (SAT/GRE): Half‑off study materials\n"
                   "• Tutoring: First session free + 50% off next 5\n"
                   "• Example: Khan Academy premium for $5/month instead of $10.",
        "keywords": ["education discount", "online course half off", "tutoring deals", "test prep coupon"]
    },
    "cruises": {
        "title": "🛳️ *CRUISES 50% OFF*",
        "details": "• Last‑minute cabins: 50% off ocean views\n"
                   "• Drink packages: BOGO on select sailings\n"
                   "• Shore excursions: Half‑off with early booking\n"
                   "• Example: 7‑night Caribbean for $399 instead of $798.",
        "keywords": ["cruise deals", "half off cruises", "last minute cruise", "BOGO cruise"]
    }
    # Add more services as needed (e.g., entertainment, shopping, etc.)
}

# ---------- UTILITY FUNCTIONS ----------
def build_menu_buttons():
    """Return the main menu inline keyboard (without Keywords)."""
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📍 Locations", callback_data="menu_locations"),
        InlineKeyboardButton("🎯 Services", callback_data="menu_services"),
        InlineKeyboardButton("📞 Contact", callback_data="menu_contact")
    )
    return markup

# ---------- BOT COMMAND HANDLERS ----------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_ids.add(message.from_user.id)
    welcome_text = (
        "👋 *Welcome to USA Half‑Off Bot!*\n\n"
        "I help you find *50% OFF* deals on food, rides, rentals, flights, hotels, medical bills, "
        "education, cruises, and more across major U.S. cities.\n\n"
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
        # Create buttons for each location
        loc_buttons = []
        for loc_key, loc_info in LOCATIONS.items():
            loc_buttons.append(InlineKeyboardButton(loc_info["name"], callback_data=f"loc_{loc_key}"))
        # Add buttons in chunks to avoid too many in a row
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
        # Contact menu with clickable links
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("💬 Primary Contact", url=f"https://t.me/{CONTACT_PRIMARY.lstrip('@')}"),
            InlineKeyboardButton("🆘 Support", url=f"https://t.me/{CONTACT_SUPPORT.lstrip('@')}"),
            InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK),
            InlineKeyboardButton("🔙 Back to Main", callback_data="back_to_main")
        )
        bot.edit_message_text(
            "📞 *Get in touch with us:*\n\nClick any button below to open a chat or join our channel.",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=markup
        )

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

    bot.answer_callback_query(call.id)

# ---------- DEFAULT HANDLER ----------
@bot.message_handler(func=lambda message: True)
def default_handler(message):
    bot.reply_to(message, "I didn't understand that. Please use the buttons below.",
                 reply_markup=build_menu_buttons())

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

# ---------- SET WEBHOOK (on Railway startup) ----------
def set_webhook():
    """Set the webhook once when the app starts."""
    time.sleep(1)  # Give time for Flask to initialize
    bot.remove_webhook()
    # Use the full webhook URL (Railway provides RAILWAY_PUBLIC_DOMAIN, or use WEBHOOK_URL env)
    full_url = f"{WEBHOOK_URL.rstrip('/')}/webhook"
    bot.set_webhook(url=full_url)
    print(f"Webhook set to {full_url}")

if __name__ == '__main__':
    # On Railway, we set the webhook once and then run Flask
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_STATIC_URL'):
        set_webhook()
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    else:
        # Local testing – use polling (no webhook)
        bot.remove_webhook()
        print("Starting polling...")
        bot.infinity_polling()
