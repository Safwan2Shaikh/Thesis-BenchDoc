"""
llm_client.py

Handles all LLM API communication
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self):
        self.api_key = os.getenv("MODEL_FARM_API_KEY")

        if not self.api_key:
            raise ValueError("❌ API key not found")

        self.deployment = "askbosch-prod-farm-openai-gpt-4o-mini-2024-07-18" 

        self.url = f"https://aoai-farm.bosch-temp.com/api/openai/deployments/{self.deployment}/chat/completions?api-version=2024-05-01-preview"

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def ask(self, messages):
        payload = {"messages": messages}

        response = requests.post(self.url, headers=self.headers, json=payload)

        if response.status_code != 200:
            return {"reply": response.text, "tokens": 0}

        data = response.json()

        return {
            "reply": data["choices"][0]["message"]["content"],
            "tokens": data.get("usage", {}).get("total_tokens", 0)
        }
