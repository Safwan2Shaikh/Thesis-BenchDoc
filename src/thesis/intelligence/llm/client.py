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
            raise ValueError("WARNING - MODEL_FARM_API_KEY not found")

        self.deployment = "askbosch-prod-farm-openai-gpt-4o-mini-2024-07-18"

        self.url = (
            f"https://aoai-farm.bosch-temp.com/api/openai/"
            f"deployments/{self.deployment}/chat/completions"
            f"?api-version=2024-05-01-preview"
        )

        self.headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }

    def ask(self, messages):

        payload = {
            "messages": messages,
            "temperature": 0.2
        }

        try:

            response = requests.post(
                self.url,
                headers=self.headers,
                json=payload,
                timeout=60
            )

            if response.status_code != 200:

                return {
                    "reply": response.text,
                    "tokens": 0
                }

            data = response.json()

            return {
                "reply": data["choices"][0]["message"]["content"],
                "tokens": data.get("usage", {}).get("total_tokens", 0)
            }

        except Exception as e:

            return {
                "reply": f"LLM Exception: {str(e)}",
                "tokens": 0
            }