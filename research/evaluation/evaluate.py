"""Evaluation runner for the research experiments.

Planned: executes the E0-E5 experiment matrix (base LLM, +RAG,
QLoRA on naive/validated synthetic QA, with/without RAG) and writes
reproducible results. Intentionally not implemented in Phase 1.
"""


def run_evaluation() -> None:
    raise NotImplementedError(
        "Evaluation experiments are planned after the research dataset phase."
    )
