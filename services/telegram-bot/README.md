# Vexa Telegram Bot

Telegram bot for Vexa meeting transcription system built with aiogram_dialog.

## Features

- 🔐 User registration and authentication
- 🤖 Create bots for meetings (Google Meet, Zoom, Teams)
- 📝 View real-time transcriptions
- 👤 User profile management
- 📊 Active bot status monitoring

## Installation

1. Create a Telegram bot via @BotFather
2. Copy `.env.example` to `.env` and fill in the variables
3. Run with Docker:

```bash
cd services/telegram-bot
docker build -t vexa-telegram-bot .
docker run --env-file .env vexa-telegram-bot
```

## Environment Variables

- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `API_GATEWAY_URL` - Vexa API Gateway URL
- `ADMIN_API_URL` - Vexa Admin API URL  
- `ADMIN_API_TOKEN` - Admin token for creating users
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

## Docker Compose Integration

Add to the main `docker-compose.yml`:

```yaml
services:
  telegram-bot:
    build: ./services/telegram-bot
    environment:
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - API_GATEWAY_URL=http://api-gateway:8000
      - ADMIN_API_URL=http://admin-api:8000
      - ADMIN_API_TOKEN=${ADMIN_API_TOKEN}
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
    depends_on:
      - postgres
      - redis
      - api-gateway
      - admin-api
```

## Usage

1. Start the bot with `/start` command
2. Enter email for registration or account linking
3. Use the menu for:
   - Creating bots for meetings
   - Viewing transcriptions
   - Managing profile

## Architecture

The bot uses aiogram_dialog to create interactive dialogs:

- `AuthSG` - authentication dialog
- `MainMenuSG` - main menu
- `MeetingsSG` - meeting and bot management
- `TranscriptionsSG` - transcription viewing
- `ProfileSG` - user profile

Integration with Vexa API happens through HTTP client that calls existing endpoints.

## Development

### Testing

Quick test without infrastructure:
```bash
cd services/telegram-bot
python test_bot.py
```

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment:
```bash
cp .env.example .env
# Edit .env with your values
```

3. Run in development mode:
```bash
python main.py
```

### Code Structure

```
app/
├── dialogs/          # aiogram_dialog definitions
│   ├── auth.py      # User authentication
│   ├── main_menu.py # Main navigation
│   ├── meetings.py  # Bot management
│   ├── transcriptions.py # Transcript viewing
│   └── profile.py   # User profile
├── services/        # Business logic
│   ├── api_client.py # Vexa API integration
│   └── user_service.py # User management
├── middlewares/     # aiogram middlewares
│   └── auth.py     # Authentication middleware
└── states.py       # Dialog states
```

## Features Status

- ✅ User authentication via email
- ✅ Bot creation for Google Meet
- ✅ Real-time transcription viewing
- ✅ User profile management
- 🚧 Zoom support (coming soon)
- 🚧 Teams support (coming soon)
- 🚧 Export transcriptions
- 🚧 Push notifications

## Troubleshooting

### Bot not responding
```bash
# Check token
echo $TELEGRAM_BOT_TOKEN

# Check logs
docker logs vexa_dev-telegram-bot-1
```

### API connection issues
```bash
# Check service availability
curl http://localhost:8056/health
curl http://localhost:8057/admin/users
```

### Database connection issues
```bash
# Check PostgreSQL
docker exec -it vexa_dev-postgres-1 psql -U postgres -d vexa -c "\dt"
``` 