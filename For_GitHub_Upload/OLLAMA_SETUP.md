# Ollama Setup Guide

This guide walks you through setting up Ollama as your AI provider for the Resume Analyzer.

## What is Ollama?

Ollama is a free, open-source tool that lets you run large language models locally on your computer. No API keys, no internet required once set up, completely free.

## System Requirements

- **Minimum**: 8GB RAM (16GB recommended)
- **Storage**: 5-10GB free space
- **Processor**: Any modern CPU (GPU support available for faster processing)

## Installation Steps

### Step 1: Download and Install Ollama

1. Go to [https://ollama.ai](https://ollama.ai)
2. Click "Download"
3. Select your operating system (Windows, Mac, or Linux)
4. Run the installer and follow the prompts
5. Allow Ollama to start automatically after installation

### Step 2: Download the Mistral Model

Open a terminal/PowerShell and run:

```bash
ollama pull mistral
```

This downloads the Mistral 7B model (~4.1GB). It may take 5-15 minutes depending on your internet speed.

### Step 3: Start Ollama Server

In a terminal, run:

```bash
ollama serve
```

You should see output like:
```
2024-01-14 10:30:45.123 Loading model 'mistral'
2024-01-14 10:30:45.456 Ollama running at http://localhost:11434
```

**Keep this terminal window open** - the Ollama server must be running while you use the Resume Analyzer.

### Step 4: Configure the Application

1. In the `backend/.env` file, set:

```dotenv
AI_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
```

2. Make sure `GROQ_API_KEY` is not required (it won't be used)

### Step 5: Start the Application

With Ollama running in another terminal:

```bash
# In your project directory
cd backend
pip install -r requirements.txt
python wsgi.py
```

The application will now use Ollama instead of Groq or Anthropic.

## Troubleshooting

### "Connection refused" or "Cannot connect to Ollama"

- Make sure you ran `ollama serve` in another terminal
- Check that Ollama is listening on `http://localhost:11434`
- On Windows, ensure the Ollama service is running

### Application is very slow

- Ollama runs on CPU by default
- If you have an NVIDIA GPU, Ollama can use CUDA for faster processing
- Visit [https://github.com/ollama/ollama](https://github.com/ollama/ollama) for GPU setup

### "model 'mistral' not found"

- Run: `ollama pull mistral` to download the model
- Wait for the download to complete

## Comparing AI Providers

| Feature | Ollama | Groq | Anthropic |
|---------|--------|------|-----------|
| Cost | Free (after download) | Free (with limits) | Paid |
| Setup | Download & run | API key only | API key required |
| Speed | Slow (CPU) | Fast | Very fast |
| Internet | Not required | Required | Required |
| API Key | No | Yes (free at console.groq.com) | Yes (paid) |
| Best for | Local, privacy-focused | Quick testing | Production use |

## Available Models in Ollama

The Resume Analyzer uses `mistral` by default. Other models available:

- `mistral` (7B) - Fast, recommended
- `llama2` (7B) - Good quality
- `neural-chat` (7B) - Optimized for conversation
- `wizard-math` (7B) - Better at reasoning

To use a different model, change `self.model` in `backend/app/services/resume_analyzer.py`

## When to Use Ollama

Choose Ollama if you:
- Want completely free operation with no ongoing costs
- Value privacy and want everything running locally
- Have a reasonably powerful computer (8GB+ RAM)
- Don't mind slightly slower responses
- Want to work offline after initial setup

## When to Use Groq

Choose Groq if you:
- Want faster responses
- Prefer cloud-based operation
- Don't want to manage local services
- Want to use the free tier without setup complexity

---

For more information: [Ollama GitHub](https://github.com/ollama/ollama)
