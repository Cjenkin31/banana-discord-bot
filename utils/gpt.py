from config.config import CLIENT


async def generate_gpt_response(model, system_story, user_input):
    if not isinstance(user_input, str):
        user_input = str(user_input)
    completion_response = CLIENT.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_story},
                {"role": "user", "content": user_input}
            ]
        )
    return completion_response.choices[0].message.content