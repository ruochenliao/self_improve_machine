#!/usr/bin/env python3
"""
✨ CSV-to-API ✨
Turn any CSV into a REST API in seconds using AI-generated code

Usage:
1. Run `python csv_to_api.py your_data.csv`
2. Define endpoints in interactive mode
3. Your API runs on http://localhost:5000

Powered by Stark-Vortex AI API: https://<your-tunnel>.trycloudflare.com
"""
import sys
import csv
from flask import Flask, jsonify

app = Flask(__name__)

def load_csv(file_path):
    data = []
    with open(file_path, 'r') as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            data.append(row)
    return data

def main():
    if len(sys.argv) != 2:
        print("Usage: python csv_to_api.py your_data.csv")
        sys.exit(1)

    csv_file = sys.argv[1]
    dataset = load_csv(csv_file)
    endpoint = input("Enter endpoint path (e.g., /data): ")

    @app.route(endpoint, methods=['GET'])
    def api_endpoint():
        return jsonify(dataset)

    print(f'\n🚀 API listening on http://localhost:5000{endpoint}')
    app.run()

if __name__ == '__main__':
    main()