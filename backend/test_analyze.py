#!/usr/bin/env python
"""Test the analyze endpoint."""
import requests
import json

url = "http://127.0.0.1:5000/api/analyze"

data = {
    "resume": """John Doe
Senior Software Engineer
john@example.com | 555-1234
LinkedIn: linkedin.com/in/johndoe

EXPERIENCE:
- Senior Software Engineer at Tech Corp (2020-present)
  * Led development of microservices architecture
  * Managed team of 5 engineers
  * Improved system performance by 40%
  
- Software Engineer at StartupXYZ (2018-2020)
  * Built REST APIs using Python/Flask
  * Implemented automated testing

SKILLS: Python, JavaScript, React, AWS, Docker, Kubernetes

EDUCATION:
- BS Computer Science, State University, 2018""",
    "job_description": """Senior Full-Stack Engineer
We're looking for a Senior Full-Stack Engineer to lead our product development.

Requirements:
- 5+ years of software development experience
- Strong proficiency in Python and JavaScript
- React or Vue.js experience
- Cloud deployment experience (AWS/GCP/Azure)
- Team leadership experience
- Docker and containerization knowledge

Nice to have:
- Kubernetes experience
- Microservices architecture knowledge
- Open source contributions"""
}

try:
    print("Sending request to /api/analyze...")
    response = requests.post(url, json=data, timeout=30)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"ERROR: {e}")
