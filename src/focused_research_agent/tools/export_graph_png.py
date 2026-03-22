import os

from focused_research_agent.graph import focused_research_agent_graph


def main():
    """Render the compiled LangGraph workflow to a PNG file."""
    os.makedirs("diagrams", exist_ok=True)

    png_bytes = focused_research_agent_graph.get_graph().draw_mermaid_png()

    out_path = os.path.join("diagrams", "graph.png")
    with open(out_path, "wb") as f:
        f.write(png_bytes)

    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()
