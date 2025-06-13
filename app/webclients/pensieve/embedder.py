from typing import List
from sentence_transformers import SentenceTransformer
from app.utils.constants import EMBEDDING_MODEL_NAME


class Embedder:

    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    def generate_vector(self, content: str) -> List[float]:
        return self.model.encode(
            content,
            show_progress_bar=True,
            convert_to_numpy=True
        ).tolist()
