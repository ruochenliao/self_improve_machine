
#!/usr/bin/env python3

import argparse
import requests
import json

def review_code(file_path: str, api_url: str):
    """
    Reads code from a file, sends it to the Prime-Zenith code-review API,
    and prints the review.
    """
    try:
        with open(file_path, 'r') as f:
            code_content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    headers = {'Content-Type': 'application/json'}
    data = {'code': code_content}

    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for HTTP errors
        review_result = response.json()
        print("Code Review Results:")
        print(json.dumps(review_result, indent=2))
    except requests.exceptions.RequestException as e:
        print(f"Error during API request: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"API Response Status: {e.response.status_code}")
            print(f"API Response Body: {e.response.text}")
    except json.JSONDecodeError:
        print("Error: Could not decode JSON response from API.")
        print(f"Raw API Response: {response.text}")

def main():
    parser = argparse.ArgumentParser(description="Review code using the Prime-Zenith AI Code Review API.")
    parser.add_argument("file_path", help="Path to the code file to review.")
    parser.add_argument("--pro", action="store_true", help="Use the PRO (GPT-4o) code review service.")
    args = parser.parse_args()

    base_api_url = "https://came-surgeons-river-exterior.trycloudflare.com/code-review"
    if args.pro:
        api_url = f"{base_api_url}-pro"
        print(f"Using PRO code review service: {api_url}")
    else:
        api_url = base_api_url
        print(f"Using standard code review service: {api_url}")

    review_code(args.file_path, api_url)

if __name__ == "__main__":
    main()
