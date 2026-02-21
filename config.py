import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
API_BASE_URL: str = os.getenv("API_BASE_URL", "http://localhost:8000")
ADMIN_CHAT_ID: int = int(os.getenv("ADMIN_CHAT_ID", "0"))
MINIAPP_URL: str = os.getenv("MINIAPP_URL", "https://example.com/miniapp")
