"""Research evaluation metrics.

Only pure, honestly-implementable helpers exist here. The full metric
suite (grounding, unsupported-claim rate, abstention accuracy) is added
with the evaluation phase; nothing is fabricated in advance.
"""


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    """Fraction of relevant items present in the top-k retrieved items."""
    if not relevant:
        raise ValueError("relevant must be non-empty")
    top_k = retrieved[:k]
    return len(set(top_k) & relevant) / len(relevant)


def exact_match(predicted: str, expected: str) -> bool:
    """Case-insensitive exact string match."""
    return predicted.strip().lower() == expected.strip().lower()
