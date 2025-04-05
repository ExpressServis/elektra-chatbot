import os
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from typing import List

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Načti produkty
try:
    with open("data/products.json", "r", encoding="utf-8") as f:
        product_data = json.load(f)
except Exception:
    product_data = []

# Načti embeddingy produktů
try:
    with open("data/products_embeddings.json", "r", encoding="utf-8") as f:
        product_embeddings = json.load(f)
except Exception:
    product_embeddings = []

# Načti statické stránky
try:
    with open("data/pages.json", "r", encoding="utf-8") as f:
        page_data = json.load(f)
except Exception:
    page_data = []

# Načti embeddingy stránek
try:
    with open("data/pages_embeddings.json", "r", encoding="utf-8") as f:
        page_embeddings = json.load(f)
except Exception:
    page_embeddings = []

# Spočítá kosinovou podobnost
def cosine_similarity(a: List[float], b: List[float]) -> float:
    a, b = np.array(a), np.array(b)
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Vytvoření embeddingu pro dotaz
def get_query_embedding(text: str) -> List[float]:
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

# Hledání nejrelevantnějších embeddingů
def find_top_matches(query: str, embeddings_data: List[dict], top_k: int = 5):
    query_vector = get_query_embedding(query)
    scored = []
    for item in embeddings_data:
        similarity = cosine_similarity(query_vector, item["embedding"])
        scored.append((similarity, item))
    scored.sort(reverse=True, key=lambda x: x[0])
    return [item for _, item in scored[:top_k]]

def is_product_query(message):
    return "baterie" in message.lower() or "displej" in message.lower() or "iphone" in message.lower()

def chat_with_openai(message):
    result = ""

    # Zkusíme najít nejrelevantnější stránky
    relevant_pages = find_top_matches(message, page_embeddings)
    if relevant_pages:
        try:
            context = "\n\n".join([p["content"] for p in relevant_pages])
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Jsi přátelský a vtipný asistent jménem Elektra. Odpovídej pouze na základě poskytnutého kontextu."},
                    {"role": "user", "content": f"Dotaz: {message}\n\nDostupný kontext:\n{context}"}
                ]
            )
            result += response.choices[0].message.content.strip()
            odkazy = [
                f'<br><a href="{p["url"]}" target="_blank" style="color:#0066cc">{p["title"]}</a>'
                for p in relevant_pages if p.get("url")
            ]
            if odkazy:
                result += "<br>" + "".join(odkazy)
        except Exception as e:
            result += f"Chyba při dotazu do AI: {str(e)}"

    # Pokud dotaz je produktový nebo nic nenalezeno, zobraz produkty
    if is_product_query(message) or not result.strip():
        relevant_products = find_top_matches(message, product_embeddings)
        if relevant_products:
            relevant_items = []
            for item in relevant_products:
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
                result += f"<br>Našla jsem tyto produkty, které by tě mohly zajímat:<br>{slider}\n\nChceš, abych ti ukázala další podobné? 🙂"

    if not result.strip():
        return "Promiň, na tohle na našem webu nemám žádné informace. Zkus to prosím jinak."

    return result.strip()
