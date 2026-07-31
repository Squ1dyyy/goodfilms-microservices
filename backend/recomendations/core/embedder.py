import asyncio
import logging
from typing import Optional
from sentence_transformers import SentenceTransformer
from recomendations.database.context import AsyncSessionLocal

logger = logging.getLogger(__name__)
model: Optional[SentenceTransformer] = None

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"


def _load_model_sync() -> SentenceTransformer:
    import torch
    torch.set_num_threads(1)
    logger.info(f"Loading embedding model '{MODEL_NAME}'...")
    m = SentenceTransformer(MODEL_NAME)
    logger.info(f"Embedding model '{MODEL_NAME}' loaded successfully.")
    return m


async def preload_model():
    """Load the embedding model in a background thread at startup."""
    global model
    try:
        model = await asyncio.to_thread(_load_model_sync)
    except Exception as e:
        logger.error(f"Failed to preload embedding model: {e}")


async def run_embeddings_generator():
    from recomendations.app.service.recommendation_service import RecommendationService
    await asyncio.sleep(5)

    while True:
        try:
            async with AsyncSessionLocal() as session:
                service = RecommendationService(session)
                has_more = await service.generate_embeddings_batch(limit=50)

            if not has_more:
                await asyncio.sleep(10)
        except Exception as e:
            logger.error(f"Error in embedding generation background task: {e}")
            await asyncio.sleep(10)

