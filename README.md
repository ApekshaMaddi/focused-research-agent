Focused Research Agent

An AI-powered research assistant built with LangGraph, designed to take a question, clarify scope, plan research, gather sources, and synthesize an answer — step by step.

🚀 What This Project Does

The agent automates a structured research workflow:

User Question → Scope → Query Planning → Search → Synthesis → Final Answer


It runs as a CLI tool (no UI yet) and processes one research request at a time.

🧠 Architecture Overview

This system uses a state graph to define every step in the research pipeline.

START
  → init_run
  → scope_question
  → generate_queries
  → search_web
  → synthesize_answer
  → finalize_run
END

Why LangGraph?

Reproducible agent behaviour

Deterministic → easier debugging

Clear input/output at every step

Scales later into multi-agent workflows

🧩 State Schema (simplified)
class ResearchState(TypedDict):
    run_id: str
    question: str
    scope: str | None
    assumptions: list[str] | None
    constraints: dict | None
    queries: list[str] | None
    sources: list[dict] | None
    answer: str | None
    citations: list[str] | None
    status: str
    errors: list[str] | None
    debug: dict | None














