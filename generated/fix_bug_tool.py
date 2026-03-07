#!/usr/bin/env python
import requests

url = 'http://localhost:8402/fix-bug'
data = {
    'code': 'def add(a, b):
    return a - b',
    'language': 'python'
}
response = requests.post(url, json=data)
print(response.json())