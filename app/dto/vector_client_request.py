from typing import Optional, Any
from pydantic import BaseModel
from app.dto.pensieve_request import PensieveRequest
from app.utils.constants import EMBEDDING_MODEL_NAME


def from_pensieve_req(req: PensieveRequest, vector: list[float]):
    return VectorClientRequest(
        collection_name=f"{req.user_id}__{EMBEDDING_MODEL_NAME.replace('/', '_')}",
        query_vector=vector,
        query_metadata=req.metadata
    )

class VectorClientRequest(BaseModel):
    collection_name: str
    query_vector: list[float]
    max_matching_records: int = 100
    query_metadata: Optional[dict[str, Any]]