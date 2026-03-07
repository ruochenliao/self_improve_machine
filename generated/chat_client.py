#!/usr/bin/env python3
import requests

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/chat'

def chat_query(query):
    response = requests.post(API_URL, json={'text': query})
    return response.json()['response']

if __name__ == '__main__':
    user_input = input('Ask me anything: ')
    print('\nResponse:\n', chat_query(user_input))