import requests
import json

# Test the job search endpoint
resume = '''
John Doe
Senior Software Engineer

Experience:
- 5 years as Full Stack Developer
- Python, JavaScript, React expertise
- Cloud architecture (AWS, GCP)
- Database design and optimization
- Team leadership experience

Skills: Python, JavaScript, React, Node.js, PostgreSQL, AWS, Docker, Kubernetes
'''

response = requests.post(
    'http://localhost:5000/api/search-jobs',
    json={'resume': resume}
)

print('Status Code:', response.status_code)
print('Response:')
print(json.dumps(response.json(), indent=2))
