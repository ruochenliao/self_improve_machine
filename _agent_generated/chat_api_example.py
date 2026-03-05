
import requests
import json

API_BASE_URL = "https://tmp-region-delicious-handbook.trycloudflare.com"

def chat_with_nova_helix(prompt):
    url = f"{API_BASE_URL}/chat"
    headers = {"Content-Type": "application/json"}
    payload = {"prompt": prompt}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

if __name__ == "__main__":
    print("Welcome to Nova-Helix Chat API Example!")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        
        print("Nova-Helix: Thinking...")
        response = chat_with_nova_helix(user_input)
        print(f"Nova-Helix: {response}")
