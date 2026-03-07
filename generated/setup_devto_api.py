#!/usr/bin/env python3
import os

api_key = input('Enter your Dev.to API key: ')
with open('config/devto_api.key', 'w') as f:
    f.write(api_key)
print('Dev.to API key configured. Restart the agent after saving.')