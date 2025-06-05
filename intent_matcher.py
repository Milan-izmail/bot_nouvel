def match_intent(text: str) -> str:
    text = text.lower()

    if "замовлення" in text or "оформити замовлення" in text:
        return "order_request"

    payment_keywords = [...]
    ...


    greeting_keywords = ["привіт", "вітаю", "доброго дня", "добрий день", "hello"]
    for word in greeting_keywords:
        if word in text:
            return "greeting"

    payment_keywords = [
        "оплата", "хочу оплатити", "можна оплатити", "сплатити",
        "потрібно виставити рахунок", "виставити посилання", "створи оплату"
    ]
    for phrase in payment_keywords:
        if phrase in text:
            return "payment_request"

    review_keywords = [
        "відгук", "надішли гугл відгук", "відгук клієнта", "залишити відгук"
    ]
    for phrase in review_keywords:
        if phrase in text:
            return "review_request"

    care_keywords = [
        "догляд", "полив", "обрізка", "як доглядати", "порада", "вода", "листя", "жовтіє", "вянe", "опадає"
    ]
    for phrase in care_keywords:
        if phrase in text:
            return "care_advice"

    thank_you_words = [
        "дякую", "дякуємо", "спасибі", "дякую вам"
    ]
    for word in thank_you_words:
        if word in text:
            return "thank_you"

    return "unknown"
