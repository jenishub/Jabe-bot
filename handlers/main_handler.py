from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show main menu."""
    keyboard = [
        [InlineKeyboardButton("✉️  Send Hotel Email", callback_data="send_email")],
        [InlineKeyboardButton("📋  Queries", callback_data="queries_menu")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        "👋 *Welcome to JB Travel Bot*\n\n"
        "What would you like to do?"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.edit_text(text, reply_markup=reply_markup, parse_mode="Markdown")


async def main_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await start(update, context)
