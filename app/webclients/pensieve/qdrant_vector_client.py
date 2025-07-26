from __future__ import annotations

from datetime import datetime
from typing import Any, List

from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import FieldCondition, Filter, MatchAny, MatchValue, Range, OrderBy, \
    QueryResponse, Direction

from app.dto.vector_client_request import VectorClientRequest
from app.dto.vector_client_response import VectorClientResponse
from app.enums.input_data_source import InputDataSource
from app.utils.application_constants import QDRANT_GRPC_URL, THRESHOLD_VECTOR_MATCHING_SCORE


def _ts(val: str | float | int) -> float:
    """Parse ISO or already‑unix timestamp → float unix timestamp."""
    if isinstance(val, (int, float)):
        return float(val)
    return datetime.fromisoformat(val).timestamp()


def _make_filter(meta: dict[str, Any] | None) -> Filter | None:
    if not meta:
        return None

    must: list[FieldCondition] = []
    for key, value in meta.items():
        if value is None:
            continue
        # range condition
        if isinstance(value, dict):
            must.append(FieldCondition(key=key, range=Range(**{k: _ts(v) for k, v in value.items()})))
        # match any
        elif isinstance(value, (list, tuple, set)):
            must.append(FieldCondition(key=key, match_any=MatchAny(any=list(value))))
        # exact match
        else:
            must.append(FieldCondition(key=key, match=MatchValue(value=value)))

    return Filter(must=must) if must else None


class QdrantVectorClient:
    def __init__(self, *, url: str | None = None):
        self._client = AsyncQdrantClient(url=url or QDRANT_GRPC_URL)

    async def fetch_latest_messages(
            self,
            *,
            collection: str,
            conversation_id: str,
            limit: int = 1,
    ) -> list[VectorClientResponse]:
        filter_query = _make_filter({"conversation_id": conversation_id})
        points, _next_offset = await self._client.scroll(
            collection_name=collection,
            scroll_filter=filter_query,
            with_payload=True,
            order_by=OrderBy(key="content_timestamp", direction=Direction.DESC),
            limit=limit,
        )
        return [self._to_dto(p) for p in points]

    async def fetch_latest_message(self, *, collection: str, conversation_id: str) -> VectorClientResponse | None:
        msgs = await self.fetch_latest_messages(collection=collection, conversation_id=conversation_id, limit=1)
        return msgs[0] if msgs else None


    async def fetch_matching_vectors(self, vector_req: VectorClientRequest) -> List[VectorClientResponse]:
        qdrant_filter = _make_filter(vector_req.query_metadata)
        scored: QueryResponse = await self._client.query_points(
            collection_name=vector_req.collection_name,
            query=vector_req.query_vector,
            query_filter=qdrant_filter,
            limit=vector_req.max_matching_records,
            with_payload=True,
            score_threshold=THRESHOLD_VECTOR_MATCHING_SCORE,
        )
        return [self._to_dto(p) for p in scored.points]


    @staticmethod
    def _to_dto(point) -> VectorClientResponse:
        pl = point.payload
        return VectorClientResponse(
            chunk_id=pl["chunk_id"],
            chunk_data_source=InputDataSource(pl["data_input_source"]),
            chunk_ingested_at=pl["ingestion_timestamp"],
            content_timestamp=pl["content_timestamp"],
            metadata={k: v for k, v in pl.items() if k not in {
                "chunk_id", "data_input_source", "ingestion_timestamp", "content_timestamp"}},
            conversation_id=pl["conversation_id"],
            message_id=pl["message_id"]
        )
