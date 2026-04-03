from sentence_transformers import SentenceTransformer
from app.core.config import settings

class EmbeddingService:
    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        self.model = SentenceTransformer(model_name)

    def generate_embedding(self, text: str):
        return self.model.encode(text)

    def generate_embeddings(self, texts: list[str]):
        return self.model.encode(texts)

embedding_service = EmbeddingService()
