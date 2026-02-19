#!/usr/bin/env python
"""Test Groq API directly."""
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('GROQ_API_KEY')
if not API_KEY:
    print("ERROR: GROQ_API_KEY environment variable not set")
    exit(1)
URL = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "llama-3.3-70b-versatile",
    "messages": [
        {
            "role": "user",
            "content": "Say hello"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 100
}

try:
    print("Testing Groq API directly...")
    print(f"URL: {URL}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    response = requests.post(URL, json=payload, headers=headers, timeout=10)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print(f"\nSuccess! Response: {json.dumps(response.json(), indent=2)}")
    
except Exception as e:
    print(f"ERROR: {e}")
