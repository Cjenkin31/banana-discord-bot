from config.config import CLIENT


def generate_gpt_response(model, story, user_input):
    if not isinstance(user_input, str):
        user_input = str(user_input)
    completion_response = CLIENT.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": story},
                {"role": "user", "content": user_input}
            ]
        )
    return completion_response.choices[0].message.content[:1999]