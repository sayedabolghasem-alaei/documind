
from app.generation.answer_generator import AnswerGenerator


answer_generator = AnswerGenerator()


query = "برای تحویل محصول در مسابقه چه چیزهایی باید آماده کنیم؟"


result = answer_generator.generate(
    query=query,
    top_k=3
)


print("\nUser Question:")
print(query)

print("\nGenerated Answer:")
print("==============================")
print(result["answer"])

print("\nSources:")
print("==============================")

for source in result["sources"]:

    print("File:", source["source"])
    print("Pages:", source["pages"])
    print("Distance:", round(source["distance"], 4))
    print("------------------------------")
