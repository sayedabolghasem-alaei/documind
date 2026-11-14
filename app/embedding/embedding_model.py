from sentence_transformers import SentenceTransformer


class EmbeddingModel:
    def __init__(self):
        self.model_name = (
            "sentence-transformers/"
            "paraphrase-multilingual-MiniLM-L12-v2"
        )

        self.model = SentenceTransformer(self.model_name)

    def encode(self, texts: list[str]):
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        return embeddings
