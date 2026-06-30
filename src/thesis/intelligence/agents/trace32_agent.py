"""
trace32_agent.py

Queries the external Trace32
Devmate Agent.
"""

import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class Trace32Agent:

    def __init__(self):
        token = os.getenv("TRACE32_AGENT_TOKEN")
        agent_id = os.getenv("TRACE32_AGENT_ID")
        self.agent_id = agent_id

        if not token:
            raise RuntimeError(
                "TRACE32_AGENT_TOKEN is not configured. Main diagnosis can continue without Trace32 specialist advice."
            )

        if not agent_id:
            raise RuntimeError(
                "TRACE32_AGENT_ID is not configured. Main diagnosis can continue without Trace32 specialist advice."
            )

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError(
                "openai package is required for Trace32Agent. Install it or disable trace32 routing."
            ) from exc

        http_client = httpx.Client(
            proxy="http://rb-proxy-apac.bosch.com:8080",
            verify=False,
        )

        self.client = OpenAI(
            api_key=token,
            base_url="https://devmate.bosch.com/api/v3",
            http_client=http_client,
        )

    def ask(self, prompt):
        try:
            response = self.client.chat.completions.create(
                model=self.agent_id,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
            )
        except Exception as exc:
            message = str(exc)
            if "Error code: 500" in message or "server_error" in message:
                raise RuntimeError(
                    "Trace32 specialist agent service returned HTTP 500/server_error. Main diagnosis can continue without Trace32 specialist advice; retry the Trace32 agent later."
                ) from exc
            raise RuntimeError(
                f"Trace32 specialist agent request failed: {message}"
            ) from exc

        return response.choices[0].message.content
