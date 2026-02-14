"""Embedding service for schema RAG using Qdrant + SentenceTransformers."""

import logging
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from config import config

logger = logging.getLogger(__name__)

# Module-level singletons (lazy-loaded)
_qdrant_client = None
_st_model = None


def _get_qdrant():
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(url=config.QDRANT_URL)
    return _qdrant_client


def _get_model():
    global _st_model
    if _st_model is None:
        _st_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _st_model


COLLECTION = "schema_embeddings"
VECTOR_SIZE = 384  # all-MiniLM-L6-v2 output dim


class EmbeddingService:
    def __init__(self):
        self.client = _get_qdrant()
        self.model = _get_model()
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            names = [c.name for c in self.client.get_collections().collections]
            if COLLECTION not in names:
                self.client.create_collection(
                    collection_name=COLLECTION,
                    vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE),
                )
                logger.info("Created Qdrant collection: %s", COLLECTION)
        except Exception as e:
            logger.error("Error ensuring collection: %s", e)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed_schema(self, table_name: str, ddl_statement: str, description: str = "") -> str:
        """Create and store an embedding for a single table schema."""
        text_to_embed = f"Table: {table_name}\n{ddl_statement}"
        if description:
            text_to_embed += f"\nDescription: {description}"

        vector = self.model.encode(text_to_embed).tolist()
        eid = str(uuid.uuid4())

        self.client.upsert(
            collection_name=COLLECTION,
            points=[
                models.PointStruct(
                    id=eid,
                    vector=vector,
                    payload={
                        "table_name": table_name,
                        "ddl_statement": ddl_statement,
                        "description": description,
                        "text": text_to_embed,
                    },
                )
            ],
        )
        logger.info("Embedded schema for table: %s", table_name)
        return eid

    def search_similar_schemas(self, query: str, limit: int = 3) -> list:
        """Search for schemas most relevant to a user query."""
        try:
            qvec = self.model.encode(query).tolist()
            hits = self.client.search(
                collection_name=COLLECTION,
                query_vector=qvec,
                limit=limit,
                with_payload=True,
            )
            return [
                {
                    "table_name": h.payload["table_name"],
                    "ddl_statement": h.payload["ddl_statement"],
                    "description": h.payload.get("description", ""),
                    "score": h.score,
                }
                for h in hits
            ]
        except Exception as e:
            logger.error("Error searching schemas: %s", e)
            return []

    def embed_all_schemas(self, schema_definitions: list):
        """Batch embed a list of {table_name, ddl_statement, description} dicts."""
        for s in schema_definitions:
            try:
                self.embed_schema(s["table_name"], s["ddl_statement"], s.get("description", ""))
            except Exception as e:
                logger.error("Failed to embed %s: %s", s["table_name"], e)

    def get_all_schemas(self) -> list:
        """Return all stored schema payloads from Qdrant."""
        try:
            result = self.client.scroll(collection_name=COLLECTION, limit=100, with_payload=True)
            points = result[0] if result else []
            return [
                {
                    "table_name": p.payload["table_name"],
                    "ddl_statement": p.payload["ddl_statement"],
                    "description": p.payload.get("description", ""),
                }
                for p in points
            ]
        except Exception as e:
            logger.error("Error listing schemas: %s", e)
            return []
