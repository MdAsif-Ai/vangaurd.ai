class FinancialService:
    """Placeholder for the deterministic calculation engine."""

    async def calculate(self, operation: str, inputs: dict[str, float]) -> float:
        raise NotImplementedError("The financial calculation engine is planned for a later phase.")

    async def compare(self, left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
        raise NotImplementedError("Financial comparison is planned for a later phase.")
