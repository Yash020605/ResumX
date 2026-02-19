#!/usr/bin/env python
"""Test career fields endpoint."""
import requests
import json
import time

time.sleep(2)  # Wait for server to start

url = "http://127.0.0.1:5000/api/career-fields"

data = {
    "resume": """John Doe
Senior Software Engineer
john@example.com | 555-1234

EXPERIENCE:
- Senior Software Engineer at Tech Corp (2020-present)
  * Led development of microservices
  * Managed team of 5 engineers
  
SKILLS: Python, JavaScript, React, AWS, Docker"""
}

try:
    print("Testing /api/career-fields...")
    response = requests.post(url, json=data, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"ERROR: {e}")
