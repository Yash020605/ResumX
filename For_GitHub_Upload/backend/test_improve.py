#!/usr/bin/env python
"""Test improve resume endpoint."""
import requests
import json
import time

time.sleep(1)

url = "http://127.0.0.1:5000/api/improve-resume"

data = {
    "resume": """John Doe
Senior Software Engineer
john@example.com

EXPERIENCE:
- Senior Software Engineer at Tech Corp (2020-present)
  * Led development of microservices
  
SKILLS: Python, JavaScript, React""",
    "job_description": """Senior Full-Stack Engineer
Requirements:
- 5+ years of software development experience
- Strong proficiency in Python and JavaScript
- React or Vue.js experience
- Cloud deployment experience (AWS/GCP/Azure)
- Team leadership experience""",
    "improvements": [
        "Add quantifiable achievements",
        "Highlight cloud experience",
        "Emphasize team leadership"
    ]
}

try:
    print("Testing /api/improve-resume...")
    response = requests.post(url, json=data, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:1000]}...")
except Exception as e:
    print(f"ERROR: {e}")
