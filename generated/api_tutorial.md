# Silent-Nexus AI API — Quickstart

Free AI-powered developer tools. No signup required!

## 1. Try Chat API
```python
import requests
url = 'https://<tunnel-not-configured>.trycloudflare.com/chat'
resp = requests.post(url, json={'query': 'Explain quantum computing'})
print(resp.json()['answer'])
```

## 2. Code Review
```python
resp = requests.post('https://<tunnel-not-configured>.trycloudflare.com/code-review', 
                   json={'code': 'def add(a,b): return a+b'})
print('Suggestions:', resp.json()['improvements'])
```

All endpoints: /docs