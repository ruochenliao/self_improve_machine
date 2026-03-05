
#!/usr/bin/env python3

import requests
import json

# Your Lucid-Helix API endpoint for code review
API_BASE_URL = "https://cet-temporal-therapist-forgot.trycloudflare.com"
CODE_REVIEW_ENDPOINT = f"{API_BASE_URL}/code-review"

def review_code(code_content: str, filename: str = "example.py") -> dict:
    """
    Sends code to the Lucid-Helix AI for a professional code review.

    Args:
        code_content: The string content of the code to be reviewed.
        filename: Optional filename for better context in the review.

    Returns:
        A dictionary containing the AI's code review, or an error message.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "code": code_content,
        "filename": filename
    }

    try:
        response = requests.post(CODE_REVIEW_ENDPOINT, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {e}"}

if __name__ == "__main__":
    # Example usage:
    sample_code = """
def calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    if count == 0:
        return 0
    return total / count

def main():
    data = [10, 20, 30, 40, 50]
    avg = calculate_average(data)
    print(f"The average is: {avg}")

if __name__ == "__main__":
    main()
"""

    print("Sending code for review...")
    review_result = review_code(sample_code, "my_script.py")

    if "error" in review_result:
        print(f"Error: {review_result['error']}")
    else:
        print("\n--- Code Review Result ---")
        print(json.dumps(review_result, indent=2))
        print("\n--------------------------")
        print(f"You can try this and other services at: {API_BASE_URL}")

    # Another example with a potential bug
    buggy_code = """
def divide(a, b):
    return a / b

print(divide(10, 0))
"""
    print("\nSending buggy code for review...")
    buggy_review_result = review_code(buggy_code, "buggy_script.py")

    if "error" in buggy_review_result:
        print(f"Error: {buggy_review_result['error']}")
    else:
        print("\n--- Buggy Code Review Result ---")
        print(json.dumps(buggy_review_result, indent=2))
        print("\n--------------------------------")
        print(f"You can try this and other services at: {API_BASE_URL}")
