# Environment Setup Examples

## Backend (.env)

### Development
```
ANTHROPIC_API_KEY=sk-ant-your_key_here
FLASK_APP=wsgi.py
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
```

### Production
```
ANTHROPIC_API_KEY=sk-ant-your_key_here
FLASK_APP=wsgi.py
FLASK_ENV=production
FLASK_DEBUG=False
PORT=5000
```

## Frontend (.env)

### Development
```
VITE_API_URL=http://localhost:5000/api
```

### Production
```
VITE_API_URL=https://api.yourdomain.com/api
```

## Docker Environment

```
# Create .env in project root
ANTHROPIC_API_KEY=sk-ant-your_key_here
```

## Getting Your Anthropic API Key

1. Visit https://console.anthropic.com
2. Sign up (free tier available)
3. Go to API Keys
4. Click "Create Key"
5. Copy the key
6. Paste in your .env file

## Important Notes

⚠️ **NEVER commit .env files to git!**
- They contain sensitive API keys
- Add to .gitignore
- Use .env.example as template

🔒 **API Key Security:**
- Keep your API key private
- Don't share in public repositories
- Rotate keys regularly
- Use environment variables in production

💡 **Best Practices:**
- Use different keys for dev and production
- Monitor API usage
- Set spending limits in console
- Use secrets management for production
