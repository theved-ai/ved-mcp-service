from abc import ABC, abstractmethod
from typing import List

from app.dto.vector_client_response import VectorClientResponse
from app.enums.input_data_source import InputDataSource
from app.webclients.pensieve.vector_text_extraction_factory import factory


class TextExtractionBase(ABC):

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        source = cls().supported_data_input_source()
        factory.register_service(cls, source)

    @abstractmethod
    def supported_data_input_source(self) -> InputDataSource:
        pass

    @abstractmethod
    async def extract_text_from_vector(self, vector_records: List[VectorClientResponse]):
        pass