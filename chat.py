import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Načti produkty
try:
    with open("data/products.json", "r", encoding="utf-8") as f:
        product_data = json.load(f)
except Exception:
    product_data = []

# Načti statické stránky
try:
    with open("data/pages.json", "r", encoding="utf-8") as f:
        page_data = json.load(f)
except Exception:
    page_data = []

def find_relevant_context(message):
    context_parts = []

    # Vyhledání v produktech
    for item in product_data:
        item_text = json.dumps(item, ensure_ascii=False)
        if any(word.lower() in item_text.lower() for word in message.split()):
            context_parts.append(item_text)

    # Vyhledání ve stránkách s bezpečnostním ošetřením
    for page in page_data:
        text = page.get("text", "")
        if any(word.lower() in text.lower() for word in message.split()):
            context_parts.append(text)

    return "\n\n".join(context_parts[:5])  # max 5 shod

def chat_with_openai(message):
    context = find_relevant_context(message)

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Jsi přátelský a vtipný asistent jménem Elektra."},
                {"role": "user", "content": f"Dotaz: {message}\n\nDostupný kontext:\n{context}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Chyba: {str(e)}"
