# How to Integrate Swift-Flux API

Use our `/generate-code` endpoint for instant Python scripts:

```python
import requests

url = 'https://<tunnel-not-configured>.trycloudflare.com/generate-code'
data = {'prompt': 'A CLI tool for CSV parsing'}
response = requests.post(url, json=data)
print(response.json()['code'])
```

👉 Try it now: [API Playground](https://<tunnel-not-configured>.trycloudflare.com)
