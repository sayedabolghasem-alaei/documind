
from app.agent.state import AgentState


def no_context_node(state: AgentState) -> dict:

    error = state.get("error", "")

    if error:
        answer = (
            "در پردازش درخواست شما خطایی رخ داد. "
            "لطفاً دوباره تلاش کنید."
        )
    else:
        answer = (
            "اطلاعات کافی برای پاسخ‌گویی به این سؤال "
            "در اسناد و Knowledge Graph پیدا نشد."
        )

    return {
        "answer": answer
    }
