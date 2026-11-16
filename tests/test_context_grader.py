from app.agent.nodes.context_grader import context_grader


def test_context_grader():

    query = "ویدیوی معرفی محصول باید چه محتوایی داشته باشد؟"

    relevant_context = """
    ویدیوی پنج دقیقه‌ای باید محصول را از ایده تا اجرا معرفی کند.
    مسئله، کاربر هدف و نقش ایجنت باید توضیح داده شوند.
    """

    irrelevant_context = """
    برای اجرای پروژه از Python و Docker استفاده می‌کنیم.
    دیتابیس PostgreSQL برای ذخیره اطلاعات مناسب است.
    """

    relevant_result = context_grader.grade(
        query=query,
        context=relevant_context
    )

    irrelevant_result = context_grader.grade(
        query=query,
        context=irrelevant_context
    )

    print("Relevant Context:", relevant_result)
    print("Irrelevant Context:", irrelevant_result)

    assert relevant_result is True
    assert irrelevant_result is False

    print("\nSemantic Context Grader test passed.")


if __name__ == "__main__":
    test_context_grader()