from typing import Type

from app.enums.input_data_source import InputDataSource
from app.webclients.pensieve.text_extraction.text_extraction_base import TextExtractionBase


class VectorTextExtractionFactory:

    def __init__(self):
        self.data_source_text_extraction_registry: dict[InputDataSource, Type[TextExtractionBase]] = {}

    def get_text_extraction_service(self, input_data_source: InputDataSource):
        if not self.data_source_text_extraction_registry.get(input_data_source):
            raise RuntimeError(f'No service registered for input source: {input_data_source}')
        return self.data_source_text_extraction_registry.get(input_data_source)()


    def register_service(self, service: Type["TextExtractionBase"], input_data_source: InputDataSource):
        if self.data_source_text_extraction_registry.get(input_data_source) is not None:
            raise RuntimeError(f'Service already registered for input source: {input_data_source}')
        self.data_source_text_extraction_registry[input_data_source] = service

factory: VectorTextExtractionFactory = VectorTextExtractionFactory()