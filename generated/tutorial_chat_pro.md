# Chat-PRO API Tutorial

Integrate the AI chat-pro service into your Python apps.

## Step 1: Install Requests
```bash
pip install requests
```

## Step 2: Make API Call
```python
import requests

response = requests.post(
    'http://localhost:8402/chat-pro',
    json={'message': 'Explain quantum computing'},
    headers={'Content-Type': 'application/json'}
)
result = response.json()['reply']
print(result)
```

## Response Example
```json
{
  "reply": "Quantum computing uses qubits...",
  "cost": 0.10
}
```

Cost: $0.10 per request | [Try now](http://localhost:8402)