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

# Jednoduchý český stemmer
def stem(word):
    endings = ['ami', 'emi', 'ovi', 'ému', 'ům', 'ích', 'ě', 'í', 'ý', 'a', 'u', 'y', 'e', 'o', 'ů']
    for end in endings:
        if word.endswith(end) and len(word) > 4:
            return word[:-len(end)]
    return word

def find_relevant_context(message):
    keywords = [stem(word.lower()) for word in message.split() if word.strip()]

    product_context = []
    product_scored = []

    # Procházení produktů a hledání shod
    for item in product_data.values():
        title = str(item.get("title", "") or "")
        description = str(item.get("description", "") or "")
        gtin = str(item.get("{http://base.google.com/ns/1.0}gtin", "") or "")
        mpn = str(item.get("{http://base.google.com/ns/1.0}mpn", "") or "")

        combined_text = f"{title} {description} {gtin} {mpn}".lower()
        combined_stemmed = " ".join([stem(word) for word in combined_text.split()])

        matches = sum(1 for keyword in keywords if keyword in combined_stemmed)
        if matches > 0:
            product_scored.append((matches, json.dumps(item, ensure_ascii=False)))

    product_scored.sort(reverse=True, key=lambda x: x[0])
    product_context += [item for _, item in product_scored[:5]]

    page_context = []
    # Procházení statických stránek a hledání shod pouze na relevantních stránkách (např. doprava)
    for page in page_data:
        full_text = f"{page.get('title', '')} {page.get('content', '')}".lower()
        full_stemmed = " ".join([stem(word) for word in full_text.split()])
        if any(keyword in full_stemmed for keyword in keywords):
            page_context.append((page.get("content", ""), page.get("url", ""), page.get("title", "")))

    return product_context, page_context[:3]

def is_product_query(message):
    # Pokud dotaz obsahuje konkrétní produkt, například "baterie iPhone 12 mini"
    return "baterie" in message.lower() and "iphone" in message.lower()

def chat_with_openai(message):
    product_context, page_context = find_relevant_context(message)

    result = ""

    # Pokud se jedná o dotaz na produkt (např. baterie pro iPhone)
    if is_product_query(message):
        if product_context:
            relevant_items = []
            for part in product_context:
                try:
                    item = json.loads(part)
                    title = item.get("title")
                    link = item.get("link")
                    image = item.get("{http://base.google.com/ns/1.0}image_link")
                    if title and link:
                        block = (
                            f'<div style="flex: 0 0 auto; width: 160px; margin-right: 10px; text-align: center; font-size: 13px;">'
                            f'<a href="{link}" target="_blank" style="text-decoration: none; color: #000;">'
                        )
                        if image:
                            block += f'<img src="{image}" alt="{title}" style="width: 100px; height: auto; border-radius: 8px;"><br>'
                        block += f'{title}</a></div>'
                        relevant_items.append(block)
                except json.JSONDecodeError:
                    continue

            if relevant_items:
                slider = (
                    "<div style='position: relative;'>"
                    "<button onclick=\"this.nextElementSibling.scrollBy({left: -300, behavior: 'smooth'})\" "
                    "style='position: absolute; left: 0; top: 40%; transform: translateY(-50%); z-index: 1; background: #eee; border: none; border-radius: 50%; width: 30px; height: 30px; cursor: pointer;'>&larr;</button>"
                    "<div style='display: flex; overflow-x: auto; gap: 10px; padding: 10px 40px; scroll-behavior: smooth;'>"
                    + "".join(relevant_items[:10]) +
                    "</div>"
                    "<button onclick=\"this.previousElementSibling.scrollBy({left: 300, behavior: 'smooth'})\" "
                    "style='position: absolute; right: 0; top: 40%; transform: translateY(-50%); z-index: 1; background: #eee; border: none; border-radius: 50%; width: 30px; height: 30px; cursor: pointer;'>&rarr;</button>"
                    "</div>"
                )
                result += f"Našla jsem tyto produkty, které by tě mohly zajímat:\n{slider}\n\nChceš, abych ti ukázala další podobné? 🙂"
            else:
                result += "Bohužel jsem nenašla žádné baterie pro iPhone 12. Zkus prosím jiný dotaz nebo se podívej na naši nabídku na webu."
        else:
            result += "Bohužel nemáme informace o baterii pro iPhone 12 mini v našem systému."

    # Pokud dotaz nesouvisí s produkty, odpovídáme na základě informací
    if not result.strip() and page_context:
        try:
            page_texts = [text for text, _, _ in page_context]
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Jsi přátelský a vtipný asistent jménem Elektra. Odpovídej pouze na základě poskytnutého kontextu."},
                    {"role": "user", "content": f"Dotaz: {message}\n\nDostupný kontext:\n{chr(10).join(page_texts)}"}
                ]
            )
            result += response.choices[0].message.content.strip()
            odkazy = [
                f'<br><a href="{url}" target="_blank" style="color:#0066cc">{title}</a>' 
                for _, url, title in page_context if url
            ]
            if odkazy:
                result += "<br>" + "".join(odkazy)
        except Exception as e:
            result += f"Chyba při dotazu do AI: {str(e)}\n"

    if not result.strip():
        return "Promiň, na tohle na našem webu nemám žádné informace. Zkus to prosím jinak."

    return result.strip()
