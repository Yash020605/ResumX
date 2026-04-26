# Migration Guide: From Anthropic to Groq/Ollama

If you were previously using the Anthropic API and want to switch to Groq or Ollama, follow this guide.

## Why Migrate?

- **Groq**: Free tier (no credit card), much faster, instant setup
- **Ollama**: Completely free, runs locally, no API calls, privacy-focused
- **Anthropic**: No longer supported in this version (use legacy version if needed)

## Quick Migration Steps

### Option 1: Switch to Groq (5 minutes)

1. **Get API Key**
   - Go to [https://console.groq.com](https://console.groq.com)
   - Sign up (takes 1 minute, no credit card)
   - Copy your API key

2. **Update .env**
   ```dotenv
   AI_PROVIDER=groq
   GROQ_API_KEY=your_groq_api_key_here
   ```

3. **Test**
   ```bash
   python wsgi.py
   ```

Done! Your application now uses Groq.

### Option 2: Switch to Ollama (15 minutes)

1. **Install Ollama**
   - Download from [https://ollama.ai](https://ollama.ai)
   - Run the installer
   - In terminal: `ollama pull mistral`

2. **Start Ollama**
   ```bash
   ollama serve
   ```
   (Keep this terminal open)

3. **Update .env**
   ```dotenv
   AI_PROVIDER=ollama
   OLLAMA_URL=http://localhost:11434
   ```

4. **Start Backend**
   ```bash
   python wsgi.py
   ```

Done! Your application now uses Ollama (locally).

## What Changed in the Code?

### Old Setup (Anthropic)
```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=2000,
    system=system_prompt,
    messages=messages
)
```

### New Setup (Groq/Ollama)
```python
import requests

# Uses HTTP requests for both providers
# Configuration in __init__() determines provider
self.ai_provider = os.getenv("AI_PROVIDER", "groq")
```

### API Changes

**All function signatures remain identical** - no changes needed in `app/routes/analysis.py` or frontend code!

- ✅ `analyze_resume_match()` - Same interface
- ✅ `generate_improved_resume()` - Same interface
- ✅ `get_career_fields()` - Same interface
- ✅ `generate_interview_prep()` - Same interface

## Troubleshooting

### "GROQ_API_KEY not set"
- Make sure `.env` file has: `GROQ_API_KEY=your_actual_key`
- Not: `GROQ_API_KEY=your_groq_api_key_here`

### "Cannot connect to Ollama"
- Make sure you ran: `ollama serve` in another terminal
- Check `.env` has: `OLLAMA_URL=http://localhost:11434`

### "Model not found" (Ollama)
- Run: `ollama pull mistral`
- Wait for download to complete

### Application is very slow (Ollama)
- Ollama runs on CPU by default
- Consider using Groq for better speed
- Or upgrade to Ollama with GPU support

## Reverting Changes

If you want to keep the old Anthropic version:

```bash
git log --oneline  # Find the commit before migration
git checkout <commit_hash> backend/app/services/resume_analyzer.py
```

Then reinstall Anthropic:
```bash
pip install anthropic==0.25.0
```

## Questions?

- **Groq Issues**: [Groq Documentation](https://console.groq.com/docs)
- **Ollama Issues**: [Ollama GitHub](https://github.com/ollama/ollama)
- **This Project**: See SETUP_GUIDE.md

---

**We recommend Groq for the best balance of speed, cost, and ease!**
