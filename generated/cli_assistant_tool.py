#!/usr/bin/env python3
"""
Bold-Phoenix CLI Assistant Tool

A simple command-line interface that uses the Bold-Phoenix AI API for intelligent conversations.
Perfect for developers who want a quick AI assistant in their terminal.

Public API: https://upgrades-approx-gadgets-hit.trycloudflare.com
"""

import requests
import json
import sys

def chat_with_ai(message, use_pro=False):
    """Send a message to the Bold-Phoenix AI API"""
    
    base_url = "https://upgrades-approx-gadgets-hit.trycloudflare.com"
    
    if use_pro:
        endpoint = "/chat-pro"
        cost = "$0.10"
    else:
        endpoint = "/chat"
        cost = "$0.01"
    
    url = base_url + endpoint
    
    payload = {
        "message": message,
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response received")
        else:
            return f"Error: {response.status_code} - {response.text}"
    
    except Exception as e:
        return f"Connection error: {str(e)}"

def main():
    print("🤖 Bold-Phoenix CLI Assistant")
    print("=" * 50)
    print("Type your message or 'quit' to exit")
    print("Type 'pro' to switch to GPT-4o mode ($0.10/request)")
    print("Type 'standard' to switch back to standard mode ($0.01/request)")
    print("=" * 50)
    
    use_pro = False
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
            
            elif user_input.lower() == 'pro':
                use_pro = True
                print("Switched to GPT-4o mode ($0.10/request)")
                continue
            
            elif user_input.lower() == 'standard':
                use_pro = False
                print("Switched to standard mode ($0.01/request)")
                continue
            
            if user_input:
                print("AI is thinking...")
                response = chat_with_ai(user_input, use_pro)
                
                mode = "GPT-4o" if use_pro else "DeepSeek"
                cost = "$0.10" if use_pro else "$0.01"
                
                print(f"\n🤖 Bold-Phoenix ({mode}, {cost}):")
                print("-" * 40)
                print(response)
                print("-" * 40)
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single message mode
        message = " ".join(sys.argv[1:])
        response = chat_with_ai(message)
        print(f"🤖 Bold-Phoenix: {response}")
    else:
        # Interactive mode
        main()