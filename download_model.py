from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

print("Model downloaded and loaded successfully!")


sentences = [
    "هوش مصنوعی چیست؟",
    "یادگیری ماشین یکی از شاخه‌های هوش مصنوعی است."
]

embeddings = model.encode(sentences)

print(embeddings.shape)