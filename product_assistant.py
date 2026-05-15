import json
import os
import re
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI


ROOT_DIR = Path(__file__).resolve().parent
PROMPTS_DIR = ROOT_DIR / "PROMPTS"

REFERENCE_FILES = [
    "PRODUCT_BOT_RULES.md",
    "BRAND_VOICE_EXAMPLES.md",
    "GOOD_PRODUCT_CARDS.md",
    "BAD_PRODUCT_PATTERNS.md",
    "PRODUCT_CARD_SCORING.md",
]

BANNED_PHRASES = [
    "ідеальний букет для кожного",
    "неперевершена композиція",
    "пориньте у світ краси",
    "найкраща якість за доступною ціною",
    "букет, який нікого не залишить байдужим",
    "чудово підійде для будь-якого свята",
    "композиція звучить",
    "виглядає свіжо, графічно і дуже виразно",
    "дарує сонячний настрій",
    "стане прекрасним доповненням",
    "підкреслить вашу індивідуальність",
]

AROMA_TERMS = [
    "nouvel amour aroma",
    "aroma",
    "аромати",
    "аромат",
    "свічки",
    "свічка",
    "дифузори",
    "дифузор",
    "ifra",
    "віск",
    "рум-спреї",
    "боді-спреї",
]

LONG_DASH_RE = re.compile("[\u2013\u2014]")

SUBSTITUTION_NOTE = (
    "У разі відсутності деяких квітів вони замінюються на аналогічні або дорожчі "
    "за рахунок компанії зі збереженням кольорової гами, стилю та ключових "
    "характеристик букета або композиції."
)

PRODUCT_CARD_SCHEMA: dict[str, Any] = {
    "name": "",
    "price": "",
    "category": "",
    "type": "",
    "short_salesbox_description": "",
    "full_shopexpress_description": "",
    "composition": "",
    "recipient": [],
    "occasion": [],
    "impression": "",
    "seo_title": "",
    "meta_description": "",
    "h1": "",
    "slug": "",
    "alt_texts": [],
    "categories": [],
    "tags": [],
    "attributes": {
        "color": "",
        "format": "",
        "size": "",
        "style": "",
        "occasion": "",
        "mood": "",
    },
    "substitution_note": "",
    "quality_score": 0,
    "quality_status": "rewrite_required",
    "quality_reason": "",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def load_reference_context() -> str:
    sections = []
    for filename in REFERENCE_FILES:
        path = ROOT_DIR / filename
        if path.exists():
            sections.append(f"# {filename}\n{read_text(path)}")
    return "\n\n".join(sections)


def load_prompt(filename: str) -> str:
    return read_text(PROMPTS_DIR / filename)


def normalize_card(card: dict[str, Any]) -> dict[str, Any]:
    normalized = json.loads(json.dumps(PRODUCT_CARD_SCHEMA, ensure_ascii=False))

    for key in normalized:
        if key in card and key != "attributes":
            normalized[key] = card[key]

    attrs = card.get("attributes") if isinstance(card.get("attributes"), dict) else {}
    for key in normalized["attributes"]:
        normalized["attributes"][key] = attrs.get(key, "") or ""

    for key in ["recipient", "occasion", "alt_texts", "categories", "tags"]:
        if isinstance(normalized[key], str):
            normalized[key] = [normalized[key]]
        elif not isinstance(normalized[key], list):
            normalized[key] = []

    return normalized


def flatten_text(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(flatten_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(flatten_text(v) for v in value)
    return str(value or "")


def has_banned_phrase(text: str) -> bool:
    lower = text.lower()
    return any(phrase in lower for phrase in BANNED_PHRASES)


def has_aroma_mention(text: str) -> bool:
    lower = text.lower()
    return any(term in lower for term in AROMA_TERMS)


def score_card(card: dict[str, Any]) -> tuple[int, str, str]:
    card = normalize_card(card)
    text = flatten_text(card)
    reasons: list[str] = []
    score = 0

    full = card["full_shopexpress_description"].lower()
    short = card["short_salesbox_description"].lower()

    brand_voice_markers = [
        "турбот",
        "жест",
        "подарунок",
        "преміаль",
        "салон",
        "момент",
        "уваг",
    ]
    if sum(1 for marker in brand_voice_markers if marker in text.lower()) >= 3:
        score += 2
    else:
        reasons.append("Недостатньо відчутний голос Nouvel Amour Flowers.")

    scenario_markers = [
        "день народження",
        "річниц",
        "подяк",
        "побач",
        "привітан",
        "освідч",
        "без приводу",
        "для мами",
        "кохан",
    ]
    if card["recipient"] and card["occasion"] and any(marker in full for marker in scenario_markers):
        score += 2
    else:
        reasons.append("Немає достатнього сценарію використання або адресата.")

    if not has_banned_phrase(text) and not ("опис фото" in full or "виконана" in full and "має" in full):
        score += 2
    else:
        reasons.append("Є шаблонна або надто описова фраза.")

    if card["seo_title"] and card["meta_description"] and card["h1"] and card["slug"]:
        score += 1
    else:
        reasons.append("Не всі SEO-поля заповнені.")

    if card["substitution_note"].strip() == SUBSTITUTION_NOTE:
        score += 1
    else:
        reasons.append("Немає точної примітки про заміну квітів.")

    composition_lower = card["composition"].lower()
    safe_unknown = "уточнюється флористом" in composition_lower or "може бути адаптован" in composition_lower
    if safe_unknown or any(word in composition_lower for word in ["троян", "півон", "тюльпан", "еустом"]):
        score += 1
    else:
        reasons.append("Склад виглядає неперевіреним або порожнім.")

    if len(short) >= 80 and len(full) >= 450 and not has_aroma_mention(text) and not LONG_DASH_RE.search(text):
        score += 1
    else:
        reasons.append("Текст ще не виглядає готовим до публікації.")

    blockers = []
    if score < 8:
        blockers.append("score нижче 8")
    if has_banned_phrase(text):
        blockers.append("є заборонені фрази")
    if has_aroma_mention(text):
        blockers.append("є згадки Aroma або суміжної тематики")
    if card["substitution_note"].strip() != SUBSTITUTION_NOTE:
        blockers.append("немає точної примітки про заміну")
    if LONG_DASH_RE.search(text):
        blockers.append("є довге тире")

    status = "approved" if not blockers else "rewrite_required"
    reason = "; ".join(blockers or reasons or ["Картка готова до публікації."])
    return score, status, reason


def apply_quality(card: dict[str, Any]) -> dict[str, Any]:
    normalized = normalize_card(card)
    score, status, reason = score_card(normalized)
    normalized["quality_score"] = score
    normalized["quality_status"] = status
    normalized["quality_reason"] = reason
    return normalized


def extract_json(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    return json.loads(cleaned)


def client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing")
    return OpenAI(api_key=api_key)


def chat_json(messages: list[dict[str, str]], temperature: float = 0.35) -> dict[str, Any]:
    response = client().chat.completions.create(
        model=os.getenv("OPENAI_TEXT_MODEL", "gpt-4o-mini"),
        messages=messages,
        response_format={"type": "json_object"},
        temperature=temperature,
    )
    content = response.choices[0].message.content or "{}"
    return extract_json(content)


def build_generation_messages(user_prompt: str) -> list[dict[str, str]]:
    system_prompt = load_prompt("product_generation_prompt.md")
    reference_context = load_reference_context()
    return [
        {
            "role": "system",
            "content": f"{system_prompt}\n\nREFERENCE CONTEXT:\n{reference_context}",
        },
        {"role": "user", "content": user_prompt},
    ]


def generate_product_card(user_prompt: str) -> dict[str, Any]:
    raw = chat_json(build_generation_messages(user_prompt), temperature=0.45)
    return apply_quality(raw)


def editor_pass(card: dict[str, Any]) -> dict[str, Any]:
    editor_prompt = load_prompt("product_editor_prompt.md")
    reference_context = load_reference_context()
    raw = chat_json(
        [
            {
                "role": "system",
                "content": f"{editor_prompt}\n\nREFERENCE CONTEXT:\n{reference_context}",
            },
            {
                "role": "user",
                "content": json.dumps(card, ensure_ascii=False, indent=2),
            },
        ],
        temperature=0.2,
    )
    improved = raw.get("improved_card") if isinstance(raw.get("improved_card"), dict) else card
    improved = apply_quality(improved)
    score = int(raw.get("score") or improved["quality_score"])
    status = raw.get("status") or improved["quality_status"]
    if improved["quality_status"] != "approved":
        status = "rewrite_required"
    return {
        "status": status if status in {"approved", "rewrite_required"} else "rewrite_required",
        "score": score,
        "reason": raw.get("reason") or improved["quality_reason"],
        "improved_card": improved,
    }


def rewrite_card(card: dict[str, Any], reason: str) -> dict[str, Any]:
    rewrite_prompt = load_prompt("product_rewrite_prompt.md")
    reference_context = load_reference_context()
    raw = chat_json(
        [
            {
                "role": "system",
                "content": f"{rewrite_prompt}\n\nREFERENCE CONTEXT:\n{reference_context}",
            },
            {
                "role": "user",
                "content": json.dumps({"reason": reason, "card": card}, ensure_ascii=False, indent=2),
            },
        ],
        temperature=0.35,
    )
    return apply_quality(raw)


def create_product_card(user_prompt: str) -> dict[str, Any]:
    generated = generate_product_card(user_prompt)
    edited = editor_pass(generated)
    card = edited["improved_card"]

    if edited["status"] != "approved" or card["quality_score"] < 8:
        card = rewrite_card(card, edited["reason"])
        edited = editor_pass(card)
        card = edited["improved_card"]

    return card


def ask_product_assistant(user_prompt: str) -> str:
    card = create_product_card(user_prompt)
    return json.dumps(card, ensure_ascii=False, indent=2)


def jardin_secret_reference_card() -> dict[str, Any]:
    return apply_quality(
        {
            "name": "Jardin Secret",
            "price": "6985 грн",
            "category": "Квіти в коробках",
            "type": "велика квіткова композиція в коробці",
            "short_salesbox_description": (
                "Велика квіткова композиція в ніжній рожевій гамі, створена для особливого "
                "привітання. Jardin Secret виглядає м'яко, дорого і дуже зібрано, це подарунок, "
                "який одразу відчувається продуманим."
            ),
            "full_shopexpress_description": (
                "Jardin Secret, велика квіткова композиція в круглій коробці для моментів, "
                "коли хочеться подарувати не просто квіти, а відчуття турботи, уваги і красивого жесту.\n\n"
                "Ніжна рожева гама створює м'який романтичний настрій, а щільна салонна форма "
                "робить композицію виразною та подарунковою. Такий формат зручно вручати, легко "
                "перевозити і приємно залишати в інтер'єрі, квіти вже оформлені як завершений подарунок.\n\n"
                "Композиція підійде для дня народження, річниці, подяки, привітання мами, коханої "
                "людини або важливої події, де потрібен подарунок із відчуттям преміальності."
            ),
            "composition": (
                "Склад уточнюється флористом. Композиція може бути адаптована відповідно до "
                "наявності квітів зі збереженням рожевої гами, пишної форми та загального враження."
            ),
            "recipient": ["для мами", "для коханої людини", "для дружини", "для подруги", "для керівниці"],
            "occasion": ["день народження", "річниця", "подяка", "освідчення", "важлива дата"],
            "impression": "ніжність, преміальність, турбота, романтика, вау-ефект без зайвої демонстративності",
            "seo_title": "Jardin Secret, квіти в коробці з доставкою по Києву",
            "meta_description": (
                "Велика квіткова композиція Jardin Secret у рожевій гамі від Nouvel Amour Flowers. "
                "Преміальна подача, доставка квітів по Києву."
            ),
            "h1": "Jardin Secret, квіткова композиція в коробці",
            "slug": "jardin-secret-flower-box",
            "alt_texts": [
                "Jardin Secret квіткова композиція в рожевій коробці",
                "Велика композиція з квітів у коробці Nouvel Amour Flowers",
                "Рожева квіткова композиція з доставкою по Києву",
                "Преміальна композиція в коробці Jardin Secret",
            ],
            "categories": [
                "Квіти в коробках",
                "Квіткові композиції",
                "Преміальні композиції",
                "Квіти на день народження",
                "Доставка квітів Київ",
            ],
            "tags": [
                "квіти в коробці",
                "рожева композиція",
                "преміальна композиція",
                "квіти Київ",
                "доставка квітів",
                "композиція для мами",
                "композиція для коханої",
            ],
            "attributes": {
                "color": "рожевий",
                "format": "композиція в коробці",
                "size": "великий",
                "style": "ніжний, преміальний, романтичний",
                "occasion": "день народження, річниця, подяка, освідчення",
                "mood": "ніжність, турбота, вау-ефект",
            },
            "substitution_note": SUBSTITUTION_NOTE,
        }
    )
