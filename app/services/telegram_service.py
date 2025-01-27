import os
from telegram import Bot
import asyncio
from dotenv import load_dotenv

load_dotenv()

class TelegramService:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.bot = Bot(token=self.bot_token)

    async def send_message(self, chat_id, message):
        """
        Send a Telegram message
        :param chat_id: Telegram chat ID or username
        :param message: Message text to send
        :return: Success status and any error message
        """
        try:
            await self.bot.send_message(chat_id=chat_id, text=message)
            return {'success': True, 'error': None}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def send_message_sync(self, chat_id, message):
        """
        Synchronous wrapper for send_message
        """
        return asyncio.run(self.send_message(chat_id, message))
