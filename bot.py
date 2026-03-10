import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ---------- CONFIG ----------
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"          # Replace with your actual token
ADMIN_ID = 1234567890                       # Replace with your Telegram user ID (optional)
CONTACT_PRIMARY = "@yourprimarycontact"
CONTACT_SUPPORT = "@yoursupport"
CHANNEL_LINK = "https://t.me/your_channel"
# ---------------------------

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# ---------- DATA (same as before) ----------
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
    },
    "rides": {
        "title": "🚗 **RIDESHARE 50% OFF**",
        "details": "• Uber: 50% off up to 10 rides (max $10 per ride)\n"
                   "• Lyft: Half‑off airport rides in FL & NJ\n"
                   "• Local taxis: 50% off first ride with code NJRIDE\n"
                   "• Example: Miami to South Beach for $5 instead of $10.",
    },
    "rent": {
        "title": "🏠 **RENT 50% OFF FIRST MONTH**",
        "details": "• Apartments in Jersey City: 50% off first month at select buildings\n"
                   "• Miami luxury condos: Half‑off security deposit\n"
                   "• Orlando student housing: 50% off first month with student ID\n"
                   "• Example: Studio in Newark for $800 first month instead of $1600.",
    },
    "shopping": {
        "title": "🛍️ **SHOPPING 50% OFF**",
        "details": "• Mall outlets: 50% off at participating stores in Sawgrass Mills (FL)\n"
                   "• Jersey Gardens (NJ): Half‑off coupon book\n"
                   "• Online code SHOP50 for extra 50% off clearance\n"
                   "• Example: Nike shoes for $40 instead of $80.",
    },
    "entertainment": {
        "title": "🎬 **ENTERTAINMENT 50% OFF**",
        "details": "• Movie tickets: BOGO at AMC Theatres (FL & NJ)\n"
                   "• Concerts: 50% off select shows at Hard Rock Live\n"
                   "• Attractions: Half‑off admission to Miami Zoo, Adventure Aquarium\n"
                   "• Example: Universal Studios tickets 50% off on Wednesdays.",
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

# ---------- MENU BUILDING ----------
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📍 Locations", callback_data="menu_locations"),
        InlineKeyboardButton("🎯 Services", callback_data="menu_services"),
        InlineKeyboardButton("📞 Contact", callback_data="menu_contact"),
        InlineKeyboardButton("🔑 Keywords", callback_data="menu_keywords")
    )
    return markup

# ---------- COMMANDS ----------
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 *Welcome to Florida & New Jersey Half‑Off Bot!*\n\n"
        "I help you find **50% OFF** deals on food, rides, rent, shopping, and entertainment "
        "across Florida and New Jersey.\n\n"
        "Choose an option below 👇"
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu())

# ---------- CALLBACKS ----------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    data = call.data

    if data == "menu_locations":
        markup = InlineKeyboardMarkup(row_width=2)
        buttons = []
        for key, loc in LOCATIONS.items():
            buttons.append(InlineKeyboardButton(loc["name"], callback_data=f"loc_{key}"))
        markup.add(*buttons)
        markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="back_main"))
        bot.edit_message_text("📍 *Select a location:*", call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    elif data == "menu_services":
        markup = InlineKeyboardMarkup(row_width=2)
        buttons = []
        for key, serv in SERVICES.items():
            buttons.append(InlineKeyboardButton(serv["title"], callback_data=f"serv_{key}"))
        markup.add(*buttons)
        markup.add(InlineKeyboardButton("🔙 Main Menu", callback_data="back_main"))
        bot.edit_message_text("🎯 *Choose a service category:*", call.message.chat.id, call.message.message_id,
                              reply_markup=markup)

    elif data == "menu_contact":
        text = (
            "📞 *Contact Information*\n\n"
            f"Primary: {CONTACT_PRIMARY}\n"
            f"Support: {CONTACT_SUPPORT}\n"
            f"Channel: {CHANNEL_LINK}\n\n"
            "Feel free to reach out!"
        )
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Main Menu", callback_data="back_main"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data == "menu_keywords":
        text = (
            "🔑 *SEO Keywords we target:*\n\n"
            "*Primary:*\n" + ", ".join(SEO_KEYWORDS["primary"]) + "\n\n"
            "*Secondary:*\n" + ", ".join(SEO_KEYWORDS["secondary"]) + "\n\n"
            "*Location‑based:*\n" + ", ".join(SEO_KEYWORDS["location_based"]) + "\n\n"
            "*Service‑based:*\n" + ", ".join(SEO_KEYWORDS["service_based"])
        )
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Main Menu", callback_data="back_main"))
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data.startswith("loc_"):
        key = data[4:]
        loc = LOCATIONS.get(key)
        if loc:
            text = f"{loc['name']}\n\n*Neighborhoods:* {', '.join(loc['neighborhoods'])}\n\n{loc['details']}"
            markup = InlineKeyboardMarkup().add(
                InlineKeyboardButton("🔙 Back to Locations", callback_data="menu_locations"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_main")
            )
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data.startswith("serv_"):
        key = data[5:]
        serv = SERVICES.get(key)
        if serv:
            text = f"{serv['title']}\n\n{serv['details']}"
            markup = InlineKeyboardMarkup().add(
                InlineKeyboardButton("🔙 Back to Services", callback_data="menu_services"),
                InlineKeyboardButton("🏠 Main Menu", callback_data="back_main")
            )
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data == "back_main":
        bot.edit_message_text("👋 *Main Menu* – choose an option:", call.message.chat.id,
                              call.message.message_id, reply_markup=main_menu())

    bot.answer_callback_query(call.id)

# ---------- DEFAULT HANDLER ----------
@bot.message_handler(func=lambda m: True)
def default(message):
    bot.reply_to(message, "Please use the buttons below.", reply_markup=main_menu())

# ---------- START POLLING ----------
if __name__ == "__main__":
    print("Bot is polling...")
    bot.infinity_polling()
