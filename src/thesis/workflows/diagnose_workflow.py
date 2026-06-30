from thesis.intelligence.orchestrator.chat_service import chat


def run(user_input: str) -> str:
    return chat(user_input)
