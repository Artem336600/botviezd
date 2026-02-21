import json
import logging
import sys
import os
from http.server import BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# Add parent directory to path so Vercel can find config.py and handlers/
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from handlers import start, finder, loser, admin

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Register routers
dp.include_router(start.router)
dp.include_router(finder.router)
dp.include_router(loser.router)
dp.include_router(admin.router)

class handler(BaseHTTPRequestHandler):
    """Vercel Serverless Function Handler"""
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            update = types.Update(**json.loads(post_data))
            
            import asyncio
            # Run the update processing in the current event loop
            asyncio.run(dp.feed_webhook_update(bot, update))
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"OK")
        except Exception as e:
            logger.error(f"Error processing update: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b"Error")
