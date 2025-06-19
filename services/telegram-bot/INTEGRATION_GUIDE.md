# Vexa Telegram Bot Integration Guide

## Integration Overview

The Telegram bot integrates with existing Vexa architecture and provides a convenient interface for:

- 🔐 User registration and authentication
- 🤖 Creating bots for meeting transcription
- 📝 Viewing real-time transcriptions
- 👤 User profile management

## Integration Architecture

```
┌─────────────────┐    HTTP    ┌─────────────────┐
│ Telegram Bot    │ ──────────→│ API Gateway     │
│ (aiogram_dialog)│            │ (FastAPI)       │
└─────────────────┘            └─────────────────┘
         │                               │
         │ PostgreSQL                    │
         ▼                               ▼
┌─────────────────┐            ┌─────────────────┐
│ Shared Models   │            │ Bot Manager     │
│ (Users, Tokens) │            │ (meetings)      │
└─────────────────┘            └─────────────────┘
```

## Integration Steps

### 1. Creating Telegram Bot

```bash
# 1. Find @BotFather in Telegram
# 2. Send /newbot
# 3. Follow the instructions
# 4. Save the bot token
```

### 2. Environment Variables Setup

Add to your `.env` file:

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
ADMIN_API_TOKEN=your_admin_token_here
```

### 3. Running with Docker Compose

Telegram bot is already added to `docker-compose.yml`. Run:

```bash
# For CPU version
cp env-example.cpu .env
# Edit .env with your tokens
make all

# For GPU version  
cp env-example.gpu .env
# Edit .env with your tokens
make all-gpu
```

### 4. Testing Integration

```bash
# Quick test without infrastructure
cd services/telegram-bot
python test_bot.py

# Check bot logs
docker logs vexa_dev-telegram-bot-1 -f
```

## Bot Functionality

### Authentication Dialog (AuthSG)
- Link Telegram account to Vexa
- Create new users
- Generate API tokens

### Main Menu (MainMenuSG)
- Navigate core functions
- Authentication status
- Help information

### Meeting Management (MeetingsSG)
- Create bots for meetings
- Platform selection (Google Meet, Zoom, Teams)
- Meeting ID validation
- Bot status monitoring

### Transcription Viewing (TranscriptionsSG)
- User meeting list
- View transcription segments
- Real-time updates

### User Profile (ProfileSG)
- Account information
- API key management
- Settings (future versions)

## Technical Details

### API Integration

Bot uses existing API endpoints:

```python
# Create user
POST /admin/users
Header: X-Admin-API-Key

# Create bot
POST /bots  
Header: X-API-Key

# Get meetings
GET /meetings
Header: X-API-Key

# Get transcription
GET /transcripts/{platform}/{meeting_id}
Header: X-API-Key
```

### Database

Telegram ID is stored in user's `data` field:

```json
{
  "telegram_id": "123456789",
  "telegram_username": "username"
}
```

### Error Handling

- HTTP API errors are displayed to user
- Data validation at dialog level
- Logging for debugging

## Extending Functionality

### Adding New Dialogs

1. Create new file in `app/dialogs/`
2. Define states in `app/states.py`
3. Add getter functions for data
4. Register dialog in `main.py`

### Notifications Integration

```python
# Example webhook handler
async def handle_meeting_completed(meeting_id: int):
    # Find user by meeting_id
    # Send notification to Telegram
    pass
```

### Adding Commands

```python
# In main.py
dp.message.register(help_command, Command("help"))
dp.message.register(status_command, Command("status"))
```

## Security

- API tokens are not displayed in full
- User validation through database
- Access control based on authentication

## Monitoring

```bash
# Bot logs
docker logs vexa_dev-telegram-bot-1

# Container status
docker ps | grep telegram-bot

# Metrics (if needed)
# Can add Prometheus metrics
```

## Troubleshooting

### Issue: Bot not responding
```bash
# Check token
echo $TELEGRAM_BOT_TOKEN

# Check logs
docker logs vexa_dev-telegram-bot-1
```

### Issue: API errors
```bash
# Check service availability
curl http://localhost:8056/health
curl http://localhost:8057/admin/users
```

### Issue: Database
```bash
# Check PostgreSQL connection
docker exec -it vexa_dev-postgres-1 psql -U postgres -d vexa -c "\dt"
```

## Future Development

- 🔔 Push notifications about meeting status
- 📊 Usage statistics
- 🎨 Enhanced UI with inline keyboards
- 🌐 Multi-language support
- 📁 Export transcriptions to files
- 🔍 Search through transcriptions
- ⚙️ Advanced bot settings 