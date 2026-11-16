import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.retrieval.reranker import Reranker


QUERY = "مستندات فنی محصول شامل چه مواردی است؟"

DOCUMENTS = [
    {"id": str(i), "text": text}
    for i, text in enumerate([
        "راهنمای کوتاه نصب و راه اندازی محصول.",
        "مستندات فنی محصول شامل معماری سیستم، ساختار پایگاه داده و API است.",
        "در این بخش درباره طراحی رابط کاربری و تجربه کاربری توضیح داده شده است.",
        "راهنمای کامل توسعه محصول شامل معماری نرم افزار، ساختار پایگاه داده، طراحی API، نحوه ارتباط سرویس ها، روش نصب، پیکربندی محیط اجرا، مدیریت خطاها و مستندات فنی هر بخش از سیستم است.",
        "ساختار پروژه و فایل های اصلی برنامه.",
        "راهنمای جامع فنی شامل توضیحات معماری، زیرساخت، API، پایگاه داده، امنیت، نصب و راه اندازی و نحوه توسعه بخش های مختلف محصول است.",
        "توضیحات مربوط به طراحی محصول و قابلیت های اصلی آن.",
        "مستندات کامل سیستم شامل معماری نرم افزار، طراحی پایگاه داده، ارتباط بین سرویس ها، مستندات API و راهنمای نصب و نگهداری است."
    ])
]


def benchmark(max_length, batch_size):

    print(f"\nmax_length={max_length}, batch_size={batch_size}")

    reranker = Reranker()

    reranker.model.max_length = max_length

    for run in range(3):

        start = time.perf_counter()

        results = reranker.model.predict(
            [
                [QUERY, document["text"]]
                for document in DOCUMENTS
            ],
            batch_size=batch_size,
            show_progress_bar=False
        )

        elapsed = time.perf_counter() - start

        print(f"Run {run + 1}: {elapsed:.4f}s")

    return results


def main():

    benchmark(max_length=512, batch_size=32)

    benchmark(max_length=256, batch_size=8)


if __name__ == "__main__":
    main()