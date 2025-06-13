from abc import ABC, abstractmethod
from typing import List

from app.dto.vector_client_request import VectorClientRequest
from app.dto.vector_client_response import VectorClientResponse


class VectorClientBase(ABC):

    @abstractmethod
    async def fetch_matching_vectors(self, vector_req: VectorClientRequest) -> List[VectorClientResponse]:
        pass