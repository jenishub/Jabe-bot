from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import get_next_jb_code, add_query
from email_sender import send_hotel_email

# Conversation states
EMAIL_HOTEL, EMAIL_GUESTS, EMAIL_CHECKIN, EMAIL_CHECKOUT, EMAIL_ROOMS = range(5)


async def email_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start email conversation - ask for hotel name and email."""
    await update.callback_query.answer()
    context.user_data.clear()
    await update.callback_query.message.edit_text(
        "✉️ *Send Hotel Email*\n\n"
        "Please enter the *hotel name and email address*:\n"
        "_(Format: Hotel Name | hotel@example.com)_",
        parse_mode="Markdown"
    )
    return EMAIL_HOTEL


async def email_hotel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save hotel info, ask for number of guests."""
    text = update.message.text.strip()
    if "|" not in text:
        await update.message.reply_text(
            "⚠️ Please use the format: *Hotel Name | hotel@example.com*",
            parse_mode="Markdown"
        )
        return EMAIL_HOTEL

    parts = text.split("|", 1)
    context.user_data["hotel_name"] = parts[0].strip()
    context.user_data["hotel_email"] = parts[1].strip()

    await update.message.reply_text(
        f"✅ Hotel: *{context.user_data['hotel_name']}*\n\n"
        "👥 How many *guests*?",
        parse_mode="Markdown"
    )
    return EMAIL_GUESTS


async def email_guests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save guests, ask for check-in date."""
    context.user_data["guests"] = update.message.text.strip()
    await update.message.reply_text(
        "📅 *Check-in date?*\n_(e.g. 15.07.2025)_",
        parse_mode="Markdown"
    )
    return EMAIL_CHECKIN


async def email_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save check-in, ask for check-out date."""
    context.user_data["checkin"] = update.message.text.strip()
    await update.message.reply_text(
        "📅 *Check-out date?*\n_(e.g. 22.07.2025)_",
        parse_mode="Markdown"
    )
    return EMAIL_CHECKOUT


async def email_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save check-out, ask for room details."""
    context.user_data["checkout"] = update.message.text.strip()
    await update.message.reply_text(
        "🛏 *Room type & category?*\n_(e.g. 2x Deluxe Double, 1x Superior Twin)_",
        parse_mode="Markdown"
    )
    return EMAIL_ROOMS


async def email_rooms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Save rooms, show confirmation."""
    context.user_data["rooms"] = update.message.text.strip()

    d = context.user_data
    keyboard = [
        [
            InlineKeyboardButton("✅ Send Email", callback_data="confirm_email"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_email"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "📋 *Please confirm the details:*\n\n"
        f"🏨 Hotel: *{d['hotel_name']}*\n"
        f"📧 Email: `{d['hotel_email']}`\n"
        f"👥 Guests: *{d['guests']}*\n"
        f"📅 Check-in: *{d['checkin']}*\n"
        f"📅 Check-out: *{d['checkout']}*\n"
        f"🛏 Rooms: *{d['rooms']}*",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )
    return EMAIL_ROOMS


async def email_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send the email and create query."""
    await update.callback_query.answer()

    if update.callback_query.data == "cancel_email":
        await update.callback_query.message.edit_text("❌ Email cancelled.")
        from handlers.main_handler import start
        await start(update, context)
        return ConversationHandler.END

    d = context.user_data
    jb_code = get_next_jb_code()

    # Send email
    success = send_hotel_email(
        jb_code=jb_code,
        hotel_email=d["hotel_email"],
        hotel_name=d["hotel_name"],
        guests=d["guests"],
        checkin=d["checkin"],
        checkout=d["checkout"],
        rooms=d["rooms"],
    )

    if success:
        # Save to fresh queries
        add_query(
            jb_code=jb_code,
            guests=d["guests"],
            checkin=d["checkin"],
            checkout=d["checkout"],
            hotel=d["hotel_name"],
            status="fresh",
        )

        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
        await update.callback_query.message.edit_text(
            f"✅ *Email sent successfully!*\n\n"
            f"📌 Reference: *{jb_code}*\n"
            f"🏨 Hotel: *{d['hotel_name']}*\n"
            f"👥 Guests: *{d['guests']}*\n"
            f"📅 {d['checkin']} → {d['checkout']}\n\n"
            f"Query *{jb_code}* added to Fresh Queries.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
        await update.callback_query.message.edit_text(
            "❌ *Failed to send email.*\n\n"
            "Please check your Gmail credentials in the `.env` file.\n"
            "Query was NOT saved.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    return ConversationHandler.END
