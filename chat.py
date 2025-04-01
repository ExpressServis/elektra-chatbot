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
    keywords = message.lower().split()

    # Vyhledání v produktech – prohledáme název, popis, EAN, produktové číslo
    for item in product_data.values():
        text_fields = [
            str(item.get("title", "") or ""),
            str(item.get("description", "") or ""),
            str(item.get("{http://base.google.com/ns/1.0}gtin", "") or ""),
            str(item.get("{http://base.google.com/ns/1.0}mpn", "") or "")
        ]
        combined_text = " ".join(text_fields).lower()
        if any(keyword in combined_text for keyword in keywords):
            context_parts.append(json.dumps(item, ensure_ascii=False))

    # Vyhledání ve stránkách
    for page in page_data:
        if any(keyword in page.get("text", "").lower() for keyword in keywords):
            context_parts.append(page["text"])

    return "\n\n".join(context_parts[:5])  # max 5 shod

def chat_with_openai(message):
    context = find_relevant_context(message)

    if not context.strip():
        return "Promiň, na tohle na našem webu nemám žádné informace. Zkus to prosím jinak."

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Jsi přátelský a vtipný asistent jménem Elektra. Odpovídej pouze na základě poskytnutého kontextu."},
                {"role": "user", "content": f"Dotaz: {message}\n\nDostupný kontext:\n{context}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Chyba: {str(e)}"
