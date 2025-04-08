import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from db import is_subscriber, add_subscriber

# --- CONFIG ---
BOT_TOKEN = "7582470455:AAFOA3jzX3oWIlr-BfMkg1TDf1BaM8AlxWI"
ADMIN_IDS = [5799529727]  # Replace with your real Telegram ID (as integer, not string)
# --- CONFIG ---

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- COMMAND HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    is_admin = user_id in ADMIN_IDS
    is_sub = is_subscriber(user_id)

    if is_sub or is_admin:
        await update.message.reply_text(
            f"👋 Hello {user.first_name}!\n\n✅ You are verified as an active subscriber.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📬 Get Insights", callback_data="get_insights")]]
            ),
            protect_content=True
        )
    else:
        await update.message.reply_text(
            "❌ You are not an active subscriber.\nPlease subscribe through our website to access premium insights.",
            protect_content=True
        )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "get_insights":
        await query.message.reply_text(
            "📊 *Today's Top Meme Coin Insights:*\n\n"
            "1. $PEPE is showing bullish volume 🔥\n"
            "2. $DOGE breakout expected 🚀\n"
            "3. $FLOKI trending in Asia 🌏",
            parse_mode="Markdown",
            protect_content=True
        )


async def insights(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📊 *Today's Top Meme Coin Insights:*\n\n"
        "1. $PEPE is showing bullish volume 🔥\n"
        "2. $DOGE breakout expected 🚀\n"
        "3. $FLOKI trending in Asia 🌏",
        parse_mode="Markdown",
        protect_content=True
    )


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔ You are not authorized to use this command.", protect_content=True)
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast Your message here...", protect_content=True)
        return

    from db import sqlite3, DB_FILE

    msg = "🚨 *Urgent Insight:*\n" + " ".join(context.args)
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM subscribers")
        users = cursor.fetchall()
        conn.close()

        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user[0], text=msg, parse_mode="Markdown", protect_content=True
                )
            except Exception as e:
                logger.warning(f"Could not send to {user[0]}: {e}")

        await update.message.reply_text("✅ Broadcast complete.", protect_content=True)
    except Exception as e:
        await update.message.reply_text(f"Broadcast error: {e}", protect_content=True)


async def block_forwarded(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg: Message = update.message
    if msg.forward_date:
        await msg.delete()


# --- MAIN ---
def main():
    from db import init_db
    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("insights", insights))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.FORWARDED, block_forwarded))

    logger.info("🚀 Elite Insights Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
