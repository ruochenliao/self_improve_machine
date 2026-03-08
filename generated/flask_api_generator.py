#!/usr/bin/env python3
# Silent-Nexus AI API Example - Generate Flask REST API
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/generate-code'

prompt = 'Create a Flask REST API for a todo list with GET/POST/PUT/DELETE endpoints'

response = requests.post(API_URL, json={'prompt': prompt}).json()
print(response['code'])