import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_gpt(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ти професійний, теплий та доброзичливий флорист з Nouvel Amour. "
                        "Відповідай лише на теми квітів, догляду, букетів, вазонів, композицій. "
                        "Не обговорюй політику, фінанси, чи сторонні теми. "
                        "Використовуй українську мову, емодзі 🌸, 🌿, 💐 де доречно."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("GPT error:", e)
        return "😔 Вибач, щось пішло не так... Спробуй, будь ласка, ще раз."
