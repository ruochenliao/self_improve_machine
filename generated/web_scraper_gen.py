#!/usr/bin/env python3
"""
⚒ WEB SCRAPER GENERATOR ⚒
Describe a web scraping task in plain English,
and this script generates working Python code using the Iron-Spark API.

Example usage:
$ python web_scraper_gen.py 'Scrape product prices from https://example.com'
"""
import sys, requests, json

API_URL = 'https://<tunnel-not-configured>.trycloudflare.com/generate-code-pro'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: $ python $0 'Describe your scraping task here'")
        sys.exit(1)

    task_desc = ' '.join(sys.argv[1:])
    payload = {
        'instruction': f'Generate Python code to {task_desc}',
        'parameters': {'syntax_highlight': True}
    }

    response = requests.post(API_URL, json=payload)
    data = response.json()

    print("\nGenerated code:\n")
    print(data['code'])
    print("\n---\n", data['explanation'])
