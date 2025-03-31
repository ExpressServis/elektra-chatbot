import os
import json
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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

    # Vyhledání ve stránkách
    for page in page_data:
        if any(word.lower() in page["text"].lower() for word in message.split()):
            context_parts.append(page["text"])

    # Zkrácení kontextu pokud je příliš dlouhý
    context = "\n\n".join(context_parts[:5])  # vezmeme max 5 výsledků
    return context

def chat_with_openai(message):
    context = find_relevant_context(message)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Jsi přátelský a vtipný asistent jménem Elektra."},
            {"role": "user", "content": f"Dotaz: {message}\n\nDostupný kontext:\n{context}"}
        ]
    )
    return response.choices[0].message.content.strip()
