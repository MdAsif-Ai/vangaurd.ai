"""Create the Qdrant collection if it does not exist.

Usage:
    python scripts/init_qdrant.py [--vector-size 1024]

The default vector size (1024) matches BGE-M3-class models; the final
dimension is fixed when embeddings land in Phase 2, at which point the
collection can be recreated.
"""

import argparse
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings  # noqa: E402
from app.integrations.qdrant import QdrantIntegration  # noqa: E402


async def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize the FinanceRAG Qdrant collection.")
    parser.add_argument(
        "--vector-size",
        type=int,
        default=1024,
        help="Embedding vector size (default: 1024).",
    )
    args = parser.parse_args()

    settings = get_settings()
    api_key = settings.qdrant_api_key.get_secret_value() if settings.qdrant_api_key else None
    integration = QdrantIntegration(url=settings.qdrant_url, api_key=api_key)
    try:
        if not await integration.ping():
            print(f"ERROR: cannot reach Qdrant at {settings.qdrant_url}")
            sys.exit(1)
        created = await integration.ensure_collection(
            settings.qdrant_collection, vector_size=args.vector_size
        )
        if created:
            print(f"Created collection '{settings.qdrant_collection}' (vector size {args.vector_size}).")
        else:
            print(f"Collection '{settings.qdrant_collection}' already exists.")
    finally:
        await integration.close()


if __name__ == "__main__":
    asyncio.run(main())