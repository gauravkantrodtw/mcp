#!/usr/bin/env python3
import sys
import json
import requests
import os

API_URL = "https://1lze1kb4t0.execute-api.eu-central-1.amazonaws.com/prod/mcp"

print("MCP proxy started", flush=True)

def main():
    for line in sys.stdin:
        try:
            req = json.loads(line)
        except json.JSONDecodeError:
            continue

        headers = {
            'Content-Type': 'application/json'
        }
        resp = requests.post(API_URL, json=req, headers=headers)
        sys.stdout.write(json.dumps(resp.json()) + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
