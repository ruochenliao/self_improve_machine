# Quickstart Guide

Use our API to boost your workflow:

```python
import requests

# Generate code with Pro:
resp = requests.post('https://<your-public-url>/generate-code-pro', json={'code': '...'})
print(resp.json())

# Free code review:
review = requests.post('https://<your-public-url>/code-review', files={'file': open('my_script.py')}).text
```

👉 Visit [our services](https://<your-public-url>) for full API docs and pricing.