import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

async def chat_with_openai(message):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Jsi přátelský a vtipný asistent jménem Elektra."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content.strip()
