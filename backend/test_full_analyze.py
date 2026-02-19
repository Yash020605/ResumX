#!/usr/bin/env python
"""Test full analyze endpoint to see the response structure."""
import requests
import json
import time

time.sleep(2)

url = "http://127.0.0.1:5000/api/analyze"

data = {
    "resume": """John Doe
Senior Software Engineer
john@example.com | 555-1234

EXPERIENCE:
- Senior Software Engineer at Tech Corp (2020-present)
  * Led development of microservices resulting in 30% performance improvement
  * Managed team of 5 engineers
  * Improved deployment speed by 40%

SKILLS: Python, JavaScript, React, AWS, Docker, Kubernetes""",
    "job_description": """Senior Full-Stack Engineer
Requirements:
- 5+ years of software development experience
- Strong proficiency in Python and JavaScript
- React or Vue.js experience
- Cloud deployment experience (AWS/GCP/Azure)
- Team leadership experience
- Docker and Kubernetes experience"""
}

try:
    print("Testing /api/analyze...")
    response = requests.post(url, json=data, timeout=60)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
