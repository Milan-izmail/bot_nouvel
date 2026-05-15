from product_assistant import ask_product_assistant


def ask_gpt(prompt: str) -> str:
    try:
        return ask_product_assistant(prompt)
    except Exception as exc:
        print("GPT error:", exc)
        return (
            "{\n"
            '  "quality_status": "rewrite_required",\n'
            '  "quality_reason": "Не вдалося згенерувати картку. Перевір OPENAI_API_KEY, prompt і формат вхідних даних."\n'
            "}"
        )
