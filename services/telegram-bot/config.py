import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable is required")

# Vexa API Configuration
API_GATEWAY_URL = os.getenv("API_GATEWAY_URL", "http://api-gateway:8000")
ADMIN_API_URL = os.getenv("ADMIN_API_URL", "http://admin-api:8001")
ADMIN_API_TOKEN = os.getenv("ADMIN_API_TOKEN")

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:password@postgres:5432/vexa")

# Redis Configuration  
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

# Bot Configuration
BOT_NAME = "Vexa Assistant"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 