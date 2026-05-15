import json
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from product_assistant import (  # noqa: E402
    LONG_DASH_RE,
    SUBSTITUTION_NOTE,
    flatten_text,
    has_aroma_mention,
    jardin_secret_reference_card,
)


def main() -> int:
    card = jardin_secret_reference_card()
    text = flatten_text(card)

    checks = {
        "quality_score_at_least_8": card["quality_score"] >= 8,
        "approved": card["quality_status"] == "approved",
        "no_long_dash": LONG_DASH_RE.search(text) is None,
        "no_aroma": not has_aroma_mention(text),
        "has_substitution_note": card["substitution_note"] == SUBSTITUTION_NOTE,
    }

    result = {
        "card": card,
        "checks": checks,
        "passed": all(checks.values()),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
