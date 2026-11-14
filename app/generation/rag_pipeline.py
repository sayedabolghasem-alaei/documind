
from app.generation.answer_generator import AnswerGenerator


class RAGPipeline:

    def __init__(self):
        self.answer_generator = AnswerGenerator()

    def run(self, query: str, top_k: int = 3) -> dict:

        result = self.answer_generator.generate(
            query=query,
            top_k=top_k
        )

        return result
