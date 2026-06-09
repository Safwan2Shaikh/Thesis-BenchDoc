import os
from dotenv import load_dotenv
import requests

# ✅ Load .env file automatically
load_dotenv()

api_key = os.getenv("MODEL_FARM_API_KEY")

url = "https://aoai-farm.bosch-temp.com/api/openai/deployments/gpt-5-nano-2025-08-07/chat/completions?api-version=2024-05-01-preview"

headers = {
    "api-key": api_key,
    "Content-Type": "application/json"
}

data = {
    "model": "gpt-5-nano-2025-08-07",
    "messages": [
        {"role": "user", "content": "Just say Hello!"}
    ]
}

response = requests.post(url, headers=headers, json=data)

print(response.json()["choices"][0]["message"]["content"])