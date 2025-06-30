from typing import Type, TYPE_CHECKING
from app.enums.input_data_source import InputDataSource


if TYPE_CHECKING:
    from .text_extraction_base import TextExtractionBase

data_source_text_extraction_registry: dict[InputDataSource, Type["TextExtractionBase"]] = {}


def get_text_extraction_service(input_data_source: InputDataSource):
    if not data_source_text_extraction_registry.get(input_data_source):
        raise RuntimeError(f'No service registered for input source: {input_data_source}')
    return data_source_text_extraction_registry.get(input_data_source)()


def register_service(service: Type["TextExtractionBase"], input_data_source: InputDataSource):
    if data_source_text_extraction_registry.get(input_data_source) is not None:
        raise RuntimeError(f'Service already registered for input source: {input_data_source}')
    data_source_text_extraction_registry[input_data_source] = service