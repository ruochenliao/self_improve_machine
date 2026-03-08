#!/usr/bin/env python3
import os
api_key = input('Enter your Dev.to API key: ')
with open('generated/.env', 'a') as f:
    f.write(f'DEVTO_API_KEY="{api_key}"
')