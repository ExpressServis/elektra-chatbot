import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import snowballstemmer

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

stemmer = snowballstemmer.stemmer("czech")

def stem(text):
    return [s for s in stemmer.stemWords(text.split())]

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
    keywords = stem(message.lower())

    for item in product_data.values():
        text = " ".join([
            str(item.get("title", "")),
            str(item.get("description", "")),
            str(item.get("{http://base.google.com/ns/1.0}gtin", "")),
            str(item.get("{http://base.google.com/ns/1.0}mpn", ""))
        ]).lower()

        stemmed_text = " ".join(stem(text))
        if all(k in stemmed_text for k in keywords):
            context_parts.append(json.dumps(item, ensure_ascii=False))

    for page in page_data:
        text = f"{page.get('title', '')} {page.get('content', '')}".lower()
        stemmed_text = " ".join(stem(text))
        if any(k in stemmed_text for k in keywords):
            context_parts.append(text)

    return "\n\n".join(context_parts[:5])

def chat_with_openai(message):
    context = find_relevant_context(message)

    if not context.strip():
        return "Promiň, na tohle na našem webu nemám žádné informace. Zkus to prosím jinak."

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
            return f"Našla jsem tyto produkty, které by tě mohly zajímat:\n{slider}\n\nChceš, abych ti ukázala další podobné? 🙂"

    except Exception as e:
        return f"Chyba při zpracování produktů: {str(e)}"

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
