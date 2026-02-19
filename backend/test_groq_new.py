#!/usr/bin/env python
"""Test Groq API with new model."""
import requests
import json

API_KEY = "REDACTED_GROQ_KEY"
URL = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama-3.1-70b-versatile",
    "messages": [
        {
            "role": "user",
            "content": "Say hello in one word"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 100
}

try:
    print("Testing Groq API with llama-3.1-70b-versatile...")
    
    response = requests.post(URL, json=payload, headers=headers, timeout=30)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Success! Response: {data['choices'][0]['message']['content']}")
    else:
        print(f"Error: {response.text}")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
