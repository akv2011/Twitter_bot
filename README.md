# Twitter Bot - AI-Powered Automated Twitter Bot

An intelligent, automated Twitter bot that leverages Claude AI for content generation and engages with target accounts automatically.

## 🚀 Features

- **Automated Content Generation**: Uses Claude AI to create engaging tweets
- **Scheduled Posting**: Post content every 2 hours, 2 days, or custom intervals
- **Account Monitoring**: Monitor target accounts and generate intelligent replies
- **OAuth 2.0 Integration**: Secure Twitter API authentication with PKCE
- **RESTful API**: Full REST API for configuration and management
- **Real-time Analytics**: Track performance and engagement metrics

## 📁 Project Structure

```
Twitter_bot/
├── src/
│   ├── api/                 # FastAPI route handlers
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── tweets.py        # Tweet management endpoints
│   │   └── config.py        # Configuration endpoints
│   └── services/            # Business logic services
│       ├── twitter_service.py  # Twitter API integration
│       └── claude_service.py   # Claude AI integration
├── config/
│   └── settings.py          # Application settings
├── tests/                   # Test files
├── .taskmaster/             # Task Master project files
├── main.py                  # FastAPI application entry point
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🛠️ Setup & Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Twitter_bot
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Configuration
Copy the example environment file and configure your API keys:
```bash
cp env.example .env
```

Edit `.env` with your credentials:
```env
# Twitter API Credentials (get from developer.twitter.com)
TWITTER_CLIENT_ID=your_twitter_client_id_here
TWITTER_CLIENT_SECRET=your_twitter_client_secret_here
TWITTER_REDIRECT_URI=http://localhost:8000/auth/callback

# Claude AI API Key (get from console.anthropic.com)
CLAUDE_API_KEY=your_claude_api_key_here

# Application Settings
SECRET_KEY=your_secret_key_here
DEBUG=True
HOST=localhost
PORT=8000
```

### 4. Run the Application
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the application is running, visit:
- **API Documentation**: `http://localhost:8000/docs`
- **Health Check**: `http://localhost:8000/health`

## 🔧 API Endpoints

### Authentication
- `GET /auth/login` - Initiate Twitter OAuth login
- `GET /auth/callback` - Handle OAuth callback
- `GET /auth/status` - Check authentication status
- `POST /auth/logout` - Logout and revoke tokens

### Tweet Management
- `POST /tweets` - Create a new tweet
- `GET /tweets/user/{user_id}` - Get user's tweets
- `POST /tweets/{tweet_id}/like` - Like a tweet
- `POST /tweets/{tweet_id}/reply` - Reply to a tweet
- `GET /tweets/timeline` - Get user's timeline

### Configuration
- `GET /config` - Get bot configuration
- `PUT /config` - Update bot configuration
- `GET /config/schedule` - Get schedule settings
- `PUT /config/schedule` - Update schedule settings
- `GET /config/targets` - Get target accounts
- `POST /config/targets` - Add target account
- `DELETE /config/targets/{username}` - Remove target account
- `POST /config/start` - Start the bot
- `POST /config/stop` - Stop the bot

## 🤖 Usage Examples

### 1. Configure the Bot
```bash
# Add a target account to monitor
curl -X POST "http://localhost:8000/config/targets" \
  -H "Content-Type: application/json" \
  -d '{"username": "elonmusk", "enabled": true, "reply_enabled": true}'

# Update posting schedule
curl -X PUT "http://localhost:8000/config/schedule" \
  -H "Content-Type: application/json" \
  -d '{"enabled": true, "interval_hours": 4, "timezone": "UTC"}'
```

### 2. Generate Content
```bash
# Create a tweet
curl -X POST "http://localhost:8000/tweets" \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello Twitter! 🚀 #AI #Bot"}'
```

### 3. Monitor Bot Status
```bash
# Check bot status
curl http://localhost:8000/config/status
```

## 🛡️ Security Features

- **OAuth 2.0 PKCE**: Secure authentication flow
- **Environment Variables**: Sensitive data stored in environment variables
- **Token Management**: Secure handling of access tokens
- **Rate Limiting**: Respects Twitter API rate limits

## 📈 Planned Features

- [ ] Database integration for persistent storage
- [ ] Advanced scheduling with cron-like expressions
- [ ] Content analytics and performance tracking
- [ ] Multi-account support
- [ ] Web dashboard for monitoring
- [ ] Docker containerization
- [ ] Webhook support for real-time events

## 🔧 Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
flake8 src/
```

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## ⚠️ Disclaimer

This bot is for educational and legitimate use cases only. Please ensure compliance with Twitter's Terms of Service and API usage policies. Be responsible with automated interactions.

## 📞 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

---

Built with ❤️ using FastAPI, Claude AI, and Twitter API v2