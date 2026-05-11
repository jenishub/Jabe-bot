from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database import (
    get_queries_by_status, get_next_jb_code, add_query,
    update_query_status, delete_query, get_query, get_all_months
)

# Conversation states
QUERY_MONTH = 10
ADD_GUESTS, ADD_CHECKIN, ADD_CHECKOUT, ADD_HOTEL = range(11, 15)

MONTH_NAMES = {
    "01": "January", "02": "February", "03": "March", "04": "April",
    "05": "May", "06": "June", "07": "July", "08": "August",
    "09": "September", "10": "October", "11": "November", "12": "December"
}


def format_query_line(q):
    return f"*{q['jb_code']}* | {q['guests']} guests | {q['checkin']}–{q['checkout']} | {q['hotel']}"


async def queries_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show queries submenu."""
    await update.callback_query.answer()
    keyboard = [
        [InlineKeyboardButton("🆕 Fresh Queries", callback_data="fresh_queries")],
        [InlineKeyboardButton("✅ Confirmed Queries", callback_data="confirmed_queries")],
        [InlineKeyboardButton("🏁 Finished Queries", callback_data="finished_queries")],
        [InlineKeyboardButton("➕ Add Query", callback_data="add_query")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")],
    ]
    await update.callback_query.message.edit_text(
        "📋 *Queries*\n\nChoose a category:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ─── FRESH QUERIES ───────────────────────────────────────────────────────────

async def fresh_queries_month(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask which month to show fresh queries for."""
    await update.callback_query.answer()
    months = get_all_months()

    if months:
        keyboard = []
        for m in months:
            parts = m.split(".")
            label = f"{MONTH_NAMES.get(parts[0], parts[0])} {parts[1]}" if len(parts) == 2 else m
            keyboard.append([InlineKeyboardButton(label, callback_data=f"noop_{m}")])
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="queries_menu")])

        await update.callback_query.message.edit_text(
            "🆕 *Fresh Queries*\n\nType the month you want to view:\n_(Format: MM.YYYY — e.g. 07.2025)_",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        await update.callback_query.message.edit_text(
            "🆕 *Fresh Queries*\n\nType the month to view:\n_(Format: MM.YYYY — e.g. 07.2025)_",
            parse_mode="Markdown"
        )
    return QUERY_MONTH


async def show_fresh_queries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show fresh queries for selected month."""
    month = update.message.text.strip()
    context.user_data["viewing_month"] = month
    queries = get_queries_by_status("fresh", month)

    parts = month.split(".")
    month_label = f"{MONTH_NAMES.get(parts[0], parts[0])} {parts[1]}" if len(parts) == 2 else month

    if not queries:
        keyboard = [[InlineKeyboardButton("🔙 Back to Queries", callback_data="queries_menu")]]
        await update.message.reply_text(
            f"🆕 *Fresh Queries — {month_label}*\n\nNo queries found for this month.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return ConversationHandler.END

    keyboard = []
    for q in queries:
        keyboard.append([InlineKeyboardButton(
            f"{q['jb_code']} | {q['guests']}pax | {q['checkin']}–{q['checkout']} | {q['hotel']}",
            callback_data=f"view_query_{q['jb_code']}_fresh"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Back to Queries", callback_data="queries_menu")])

    await update.message.reply_text(
        f"🆕 *Fresh Queries — {month_label}* ({len(queries)} total)\n\nTap a query to manage it:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return ConversationHandler.END


# ─── CONFIRMED QUERIES ────────────────────────────────────────────────────────

async def confirmed_queries_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all confirmed queries."""
    await update.callback_query.answer()
    queries = get_queries_by_status("confirmed")

    if not queries:
        keyboard = [[InlineKeyboardButton("🔙 Back to Queries", callback_data="queries_menu")]]
        await update.callback_query.message.edit_text(
            "✅ *Confirmed Queries*\n\nNo confirmed queries yet.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    keyboard = []
    for q in queries:
        keyboard.append([InlineKeyboardButton(
            f"{q['jb_code']} | {q['guests']}pax | {q['checkin']}–{q['checkout']} | {q['hotel']}",
            callback_data=f"view_query_{q['jb_code']}_confirmed"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Back to Queries", callback_data="queries_menu")])

    await update.callback_query.message.edit_text(
        f"✅ *Confirmed Queries* ({len(queries)} total)\n\nTap a query to manage it:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ─── FINISHED QUERIES ─────────────────────────────────────────────────────────

async def finished_queries_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all finished queries."""
    await update.callback_query.answer()
    queries = get_queries_by_status("finished")

    if not queries:
        keyboard = [[InlineKeyboardButton("🔙 Back to Queries", callback_data="queries_menu")]]
        await update.callback_query.message.edit_text(
            "🏁 *Finished Queries*\n\nNo finished queries yet.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    keyboard = []
    for q in queries:
        keyboard.append([InlineKeyboardButton(
            f"{q['jb_code']} | {q['guests']}pax | {q['checkin']}–{q['checkout']} | {q['hotel']}",
            callback_data=f"view_query_{q['jb_code']}_finished"
        )])
    keyboard.append([InlineKeyboardButton("🔙 Back to Queries", callback_data="queries_menu")])

    await update.callback_query.message.edit_text(
        f"🏁 *Finished Queries* ({len(queries)} total)\n\nTap a query to manage it:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ─── QUERY ACTION (view/move/delete) ─────────────────────────────────────────

async def query_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle view/delete/move actions on a query."""
    await update.callback_query.answer()
    data = update.callback_query.data  # e.g. "view_query_JB001_fresh"

    parts = data.split("_")
    action = parts[0]           # view / delete / move
    jb_code = parts[2]          # JB001
    origin = parts[3] if len(parts) > 3 else "fresh"  # fresh / confirmed / finished

    if action == "view":
        q = get_query(jb_code)
        if not q:
            await update.callback_query.message.edit_text("Query not found.")
            return

        text = (
            f"📌 *{jb_code}*\n\n"
            f"👥 Guests: *{q['guests']}*\n"
            f"📅 Check-in: *{q['checkin']}*\n"
            f"📅 Check-out: *{q['checkout']}*\n"
            f"🏨 Hotel: *{q['hotel']}*\n"
            f"📊 Status: *{q['status'].capitalize()}*\n"
            f"🕐 Created: {q['created_at']}"
        )

        keyboard = []
        if origin == "fresh":
            keyboard.append([InlineKeyboardButton(
                "✅ Move to Confirmed", callback_data=f"move_{jb_code}_{origin}_confirmed"
            )])
        elif origin == "confirmed":
            keyboard.append([InlineKeyboardButton(
                "🏁 Move to Finished", callback_data=f"move_{jb_code}_{origin}_finished"
            )])

        keyboard.append([InlineKeyboardButton(
            "🗑 Delete Query", callback_data=f"delete_{jb_code}_{origin}"
        )])

        back_target = f"{origin}_queries" if origin != "fresh" else "queries_menu"
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data=f"{origin}_queries_back")])
        keyboard.append([InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")])

        await update.callback_query.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif action == "delete":
        delete_query(jb_code)
        back_cb = "queries_menu"
        keyboard = [[InlineKeyboardButton("🔙 Back to Queries", callback_data=back_cb)]]
        await update.callback_query.message.edit_text(
            f"🗑 *{jb_code}* has been deleted.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    elif action == "move":
        # parts: move_JB001_fresh_confirmed
        new_status = parts[4] if len(parts) > 4 else parts[3]
        update_query_status(jb_code, new_status)

        status_emoji = {"confirmed": "✅", "finished": "🏁"}.get(new_status, "📌")
        keyboard = [[InlineKeyboardButton("🔙 Back to Queries", callback_data="queries_menu")]]
        await update.callback_query.message.edit_text(
            f"{status_emoji} *{jb_code}* moved to *{new_status.capitalize()} Queries*.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


# ─── ADD QUERY ────────────────────────────────────────────────────────────────

async def add_query_guests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start add query flow - ask for guests."""
    await update.callback_query.answer()
    context.user_data.clear()
    await update.callback_query.message.edit_text(
        "➕ *Add Query*\n\n👥 Number of guests?",
        parse_mode="Markdown"
    )
    return ADD_GUESTS


async def add_query_checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["guests"] = update.message.text.strip()
    await update.message.reply_text(
        "📅 *Check-in date?*\n_(e.g. 15.07.2025)_",
        parse_mode="Markdown"
    )
    return ADD_CHECKIN


async def add_query_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["checkin"] = update.message.text.strip()
    await update.message.reply_text(
        "📅 *Check-out date?*\n_(e.g. 22.07.2025)_",
        parse_mode="Markdown"
    )
    return ADD_CHECKOUT


async def add_query_hotel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["checkout"] = update.message.text.strip()
    await update.message.reply_text(
        "🏨 *Hotel name?*\n_(Type 'TBD' or any name if not confirmed yet)_",
        parse_mode="Markdown"
    )
    return ADD_HOTEL


async def add_query_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hotel"] = update.message.text.strip()
    d = context.user_data
    jb_code = get_next_jb_code()

    add_query(
        jb_code=jb_code,
        guests=d["guests"],
        checkin=d["checkin"],
        checkout=d["checkout"],
        hotel=d["hotel"],
        status="fresh",
    )

    keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]]
    await update.message.reply_text(
        f"✅ *Query added to Fresh Queries!*\n\n"
        f"📌 Reference: *{jb_code}*\n"
        f"👥 Guests: *{d['guests']}*\n"
        f"📅 {d['checkin']} → {d['checkout']}\n"
        f"🏨 Hotel: *{d['hotel']}*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )
    return ConversationHandler.END
