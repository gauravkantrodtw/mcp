#!/usr/bin/env python3
import sys
import json
import requests
import os

API_URL = "https://wnu8q212td.execute-api.eu-central-1.amazonaws.com/prod/mcp"
API_TOKEN = os.environ.get('API_TOKEN', 'your_token_here')

print("MCP proxy started", flush=True)

def main():
    for line in sys.stdin:
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        headers = {
            'Authorization': f'Bearer {API_TOKEN}',
            'Content-Type': 'application/json'
        }
        resp = requests.post(API_URL, json=req, headers=headers)
        sys.stdout.write(json.dumps(resp.json()) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
