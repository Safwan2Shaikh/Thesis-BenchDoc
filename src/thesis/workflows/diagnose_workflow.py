from thesis.intelligence.orchestrator.chat_service import chat


def run(
    user_input: str,
    selected_bench: str = None,
    general_session: bool = False,
    include_external_agents: bool = True,
    include_general_chunks: bool = True
) -> str:
    return chat(
        user_input,
        selected_bench=selected_bench,
        general_session=general_session,
        include_external_agents=include_external_agents,
        include_general_chunks=include_general_chunks
    )
