import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from apps.notifications.services.telegram_link_service import TelegramLinkService
from apps.notifications.models import TelegramLink
from apps.accounts.models import CustomUser

logger = logging.getLogger(__name__)


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to the Nexus bot! Send the 6-digit code from your "
        "Nexus account settings to link this chat."
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    chat_id = update.effective_chat.id

    if not (text.isdigit() and len(text) == 6):
        await update.message.reply_text("Please send a valid 6-digit code.")
        return

    from channels.db import database_sync_to_async

    @database_sync_to_async
    def link_account(code, chat_id):
        user_id = TelegramLinkService.resolve_code(code)
        if user_id is None:
            return False
        user = CustomUser.objects.get(id=user_id)
        TelegramLink.objects.update_or_create(
            user=user, defaults={"chat_id": chat_id}
        )
        return True

    success = await link_account(text, chat_id)

    if success:
        await update.message.reply_text("✅ Your Nexus account is now linked!")
        logger.info(f"Telegram account linked for chat_id ending in ...{str(chat_id)[-4:]}")
    else:
        await update.message.reply_text("❌ Invalid or expired code. Please generate a new one.")


class Command(BaseCommand):
    help = "Runs the Telegram bot in polling mode. Must run as a separate process."

    def handle(self, *args, **options):
        application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
        application.add_handler(CommandHandler("start", start_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

        self.stdout.write(self.style.SUCCESS("Telegram bot started (polling mode)..."))
        application.run_polling()