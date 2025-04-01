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
        title = str(item.get("title", "") or "")
        description = str(item.get("description", "") or "")
        gtin = str(item.get("{http://base.google.com/ns/1.0}gtin", "") or "")
        mpn = str(item.get("{http://base.google.com/ns/1.0}mpn", "") or "")

        combined_text = f"{title} {description} {gtin} {mpn}".lower()
        if all(keyword in combined_text for keyword in keywords):
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

    # Pokusíme se extrahovat produkty z kontextu
    try:
        relevant_items = []
        for part in context.split("\n\n"):
            try:
                item = json.loads(part)
                title = item.get("title")
                link = item.get("link")
                image = item.get("{http://base.google.com/ns/1.0}image_link")
                if title and link:
                    if image:
                        relevant_items.append(f'<div style="flex: 0 0 auto; width: 160px; margin-right: 10px; text-align: center; font-size: 13px;">'
                                               f'<a href="{link}" target="_blank" style="text-decoration: none; color: #000;">'
                                               f'<img src="{image}" alt="{title}" style="width: 100px; height: auto; border-radius: 8px;"><br>{title}'
                                               f'</a></div>')
                    else:
                        relevant_items.append(f'<div style="flex: 0 0 auto; width: 160px; margin-right: 10px; text-align: center; font-size: 13px;">'
                                               f'<a href="{link}" target="_blank">{title}</a></div>')
            except json.JSONDecodeError:
                continue

        if relevant_items:
            slider = ("<div style='display: flex; overflow-x: auto; gap: 10px; padding: 10px 0;'>"
                      + "".join(relevant_items[:10]) + "</div>")
            return f"Našla jsem tyto produkty, které by tě mohly zajímat:
{slider}\n\nChceš, abych ti ukázala další podobné? 🙂"

    except Exception as e:
        return f"Chyba při zpracování produktů: {str(e)}"

    # Pokud nenajdeme produkty, pošleme dotaz do AI s kontextem
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
