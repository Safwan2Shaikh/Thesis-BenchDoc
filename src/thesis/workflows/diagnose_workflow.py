from thesis.intelligence.orchestrator.chat_service import chat


def run(user_input: str, selected_bench: str = None, general_session: bool = False) -> str:
    return chat(
        user_input,
        selected_bench=selected_bench,
        general_session=general_session
    )
