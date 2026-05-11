import logging
import os
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ConversationHandler
)
from handlers.email_handler import (
    email_start, email_hotel, email_guests, email_checkin,
    email_checkout, email_rooms, email_confirm, EMAIL_HOTEL,
    EMAIL_GUESTS, EMAIL_CHECKIN, EMAIL_CHECKOUT, EMAIL_ROOMS
)
from handlers.query_handler import (
    queries_menu, fresh_queries_month, show_fresh_queries,
    query_action, add_query_guests, add_query_checkin,
    add_query_checkout, add_query_hotel, add_query_confirm,
    confirmed_queries_menu, finished_queries_menu,
    QUERY_MONTH, ADD_GUESTS, ADD_CHECKIN, ADD_CHECKOUT, ADD_HOTEL
)
from handlers.main_handler import start, main_menu_callback

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# Railway injects PORT automatically; Telegram webhook needs a public HTTPS URL.
# Set WEBHOOK_URL in Railway variables to your Railway app domain, e.g.:
#   https://jb-travel-bot-production.up.railway.app
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "").rstrip("/")
PORT = int(os.getenv("PORT", 8443))


def build_app():
    app = Application.builder().token(BOT_TOKEN).build()

    # ── Email sending conversation ──────────────────────────────────────────
    email_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(email_start, pattern="^send_email$")],
        states={
            EMAIL_HOTEL:   [MessageHandler(filters.TEXT & ~filters.COMMAND, email_hotel)],
            EMAIL_GUESTS:  [MessageHandler(filters.TEXT & ~filters.COMMAND, email_guests)],
            EMAIL_CHECKIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_checkin)],
            EMAIL_CHECKOUT:[MessageHandler(filters.TEXT & ~filters.COMMAND, email_checkout)],
            EMAIL_ROOMS:   [MessageHandler(filters.TEXT & ~filters.COMMAND, email_rooms)],
        },
        fallbacks=[CommandHandler("cancel", start)],
        allow_reentry=True,
    )

    # ── Add query conversation ──────────────────────────────────────────────
    add_query_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(add_query_guests, pattern="^add_query$")],
        states={
            ADD_GUESTS:  [MessageHandler(filters.TEXT & ~filters.COMMAND, add_query_checkin)],
            ADD_CHECKIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_query_checkout)],
            ADD_CHECKOUT:[MessageHandler(filters.TEXT & ~filters.COMMAND, add_query_hotel)],
            ADD_HOTEL:   [MessageHandler(filters.TEXT & ~filters.COMMAND, add_query_confirm)],
        },
        fallbacks=[CommandHandler("cancel", start)],
        allow_reentry=True,
    )

    # ── Fresh queries month selection ───────────────────────────────────────
    fresh_month_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(fresh_queries_month, pattern="^fresh_queries$")],
        states={
            QUERY_MONTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, show_fresh_queries)],
        },
        fallbacks=[CommandHandler("cancel", start)],
        allow_reentry=True,
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(email_conv)
    app.add_handler(add_query_conv)
    app.add_handler(fresh_month_conv)

    app.add_handler(CallbackQueryHandler(main_menu_callback,       pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(queries_menu,             pattern="^queries_menu$"))
    app.add_handler(CallbackQueryHandler(confirmed_queries_menu,   pattern="^confirmed_queries$"))
    app.add_handler(CallbackQueryHandler(finished_queries_menu,    pattern="^finished_queries$"))
    app.add_handler(CallbackQueryHandler(query_action,             pattern="^(delete|move|view)_query_"))
    app.add_handler(CallbackQueryHandler(email_confirm,            pattern="^(confirm_email|cancel_email)$"))

    return app


def main():
    app = build_app()

    if WEBHOOK_URL:
        # ── Webhook mode (Railway / any HTTPS host) ─────────────────────────
        logger.info(f"Starting webhook on port {PORT} → {WEBHOOK_URL}")
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            webhook_url=f"{WEBHOOK_URL}/telegram",
            url_path="/telegram",
            drop_pending_updates=True,
        )
    else:
        # ── Polling mode (local development) ────────────────────────────────
        logger.info("WEBHOOK_URL not set — starting in polling mode (local dev)")
        app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
