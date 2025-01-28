from config.config import DEEPSEEK_CLIENT
from typing import Any

DEEPSEEK_MODEL = "deepseek-chat"
ROLE_SYSTEM = "system"
ROLE_USER = "user"

async def generate_deepseek_response(_model: str, system_story: str, user_input: Any) -> str:
    if not isinstance(user_input, str):
        user_input = str(user_input)

    try:
        completion_response = DEEPSEEK_CLIENT.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": ROLE_SYSTEM, "content": system_story},
                {"role": ROLE_USER, "content": user_input}
            ],
            stream=False
        )
        return completion_response.choices[0].message.content
    except Exception as e:
        return f"Failed to generate deepseek response: {e}"