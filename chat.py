import os
import openai
import json
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Načti produkty ze souboru
try:
    with open("data/products.json", "r", encoding="utf-8") as f:
        products = json.load(f)
except FileNotFoundError:
    products = []

def search_products(query):
    query = query.lower()
    results = []

    for product in products:
        text_fields = [
            product.get("title", ""),
            product.get("description", ""),
            product.get("brand", ""),
            product.get("category", ""),
            product.get("ean", ""),
            product.get("sku", ""),
        ]
        combined_text = " ".join(text_fields).lower()
        if query in combined_text:
            results.append(product)

    return results[:5]  # max 5 výsledků

def chat_with_openai(message):
    matched = search_products(message)
    if matched:
        response = "Našel jsem tyto produkty:\n\n"
        for p in matched:
            response += f"📦 **{p.get('title', 'Bez názvu')}**\n"
            response += f"💰 Cena: {p.get('price', 'Neznámá')} Kč\n"
            response += f"🔗 [Otevřít produkt]({p.get('link', '#')})\n\n"
        return response.strip()

    # fallback na OpenAI
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Jsi přátelský a vtipný asistent jménem Elektra."},
            {"role": "user", "content": message}
        ]
    )
    return completion.choices[0].message.content.strip()
