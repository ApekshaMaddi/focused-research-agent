# CLI entrypoint (python -m focused_research_agent.cli)
from focused_research_agent.state import ResearchState
from focused_research_agent.graph import focused_research_agent_graph

def make_initial_state(question:str) -> ResearchState:
    """
    Create the starting state for the research agent run.
    """

    initial_state: ResearchState = {
        "run_id": "",  # set by init_run node
        "question": question,  # user input

        # Scoping
        "scope": None,
        "assumptions": None,
        "constraints": None,

        # Planning
        "queries": None,

        # Search results
        "sources": None,

        # Synthesis
        "answer": None,
        "citations": None,

        # Operational
        "status": "started",
        "errors": [],
        "debug": None,
    }

    return initial_state

if __name__ == "__main__":
    user_question = input("What is your question? ").strip()
    initial_state = make_initial_state(user_question)

    final_state = focused_research_agent_graph.invoke(initial_state)
    print(final_state)


