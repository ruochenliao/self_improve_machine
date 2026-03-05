
import requests
import json

API_URL = "https://originally-governance-determined-standard.trycloudflare.com/summarize"

def summarize_text(text):
    headers = {"Content-Type": "application/json"}
    payload = {"text": text}
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

if __name__ == "__main__":
    example_text = """
    Artificial intelligence (AI) is intelligence demonstrated by machines,
    as opposed to the natural intelligence displayed by humans and animals.
    Leading AI textbooks define the field as the study of "intelligent agents":
    any device that perceives its environment and takes actions that maximize
    its chance of successfully achieving its goals. Colloquially, the term "artificial intelligence"
    is often used to describe machines that mimic "cognitive" functions that humans associate
    with the human mind, such as "learning" and "problem-solving".
    """
    summary_result = summarize_text(example_text)
    if "summary" in summary_result:
        print("Summary:")
        print(summary_result["summary"])
    else:
        print("Error:", summary_result.get("error", "Unknown error"))
