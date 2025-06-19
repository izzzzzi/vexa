#!/usr/bin/env python3
"""
Quick test script for Vexa Telegram Bot
Run this to test basic functionality without full infrastructure
"""

import asyncio
import logging
from unittest.mock import AsyncMock

# Mock the dependencies for testing
import sys
sys.path.append('.')

logging.basicConfig(level=logging.INFO)

async def test_dialogs():
    """Test dialog structure without dependencies"""
    print("🧪 Testing Vexa Telegram Bot dialogs...")
    
    # Test dialog imports
    try:
        from app.dialogs.auth import auth_dialog
        from app.dialogs.main_menu import main_menu_dialog
        from app.dialogs.meetings import meetings_dialog
        from app.dialogs.transcriptions import transcriptions_dialog
        from app.dialogs.profile import profile_dialog
        print("✅ All dialogs imported successfully")
    except Exception as e:
        print(f"❌ Dialog import failed: {e}")
        return False
    
    # Test states
    try:
        from app.states import AuthSG, MainMenuSG, MeetingsSG, TranscriptionsSG, ProfileSG
        print("✅ All states imported successfully")
    except Exception as e:
        print(f"❌ States import failed: {e}")
        return False
    
    # Test services (will fail without real infrastructure, but we can test imports)
    try:
        from app.services.api_client import VexaAPIClient
        from app.services.user_service import UserService
        print("✅ Services imported successfully")
    except Exception as e:
        print(f"❌ Services import failed: {e}")
        return False
    
    print("🎉 All basic tests passed!")
    print("\n📋 Next steps:")
    print("1. Get Telegram bot token from @BotFather")
    print("2. Set TELEGRAM_BOT_TOKEN in .env")
    print("3. Start the full Vexa infrastructure with: make all")
    print("4. Add telegram-bot service to docker-compose.yml")
    print("5. Test with real Telegram bot")
    
    return True

if __name__ == "__main__":
    asyncio.run(test_dialogs()) 