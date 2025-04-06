import os
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from typing import List
from faiss_utils import load_index, search_similar

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Načti data
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

product_embeddings = load_json("data/products_embeddings.json")
page_embeddings = load_json("data/pages_embeddings.json")

try:
    product_index = load_index("data/faiss_product_index.bin")
except Exception:
    product_index = None

try:
    page_index = load_index("data/faiss_page_index.bin")
except Exception:
    page_index = None

# Vytvoření embeddingu pro dotaz
def get_query_embedding(text: str) -> List[float]:
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

# Vyhledávání pomocí Faiss
def find_top_matches_faiss(query: str, index, embeddings_data: List[dict], top_k: int = 5):
    if index is None:
        return []
    query_vector = get_query_embedding(query)
    query_np = np.array(query_vector, dtype=np.float32).reshape(1, -1)
    distances, indices = search_similar(query_np, index, top_k)
    return [embeddings_data[i] for i in indices[0]]

def is_product_query(message):
    return "baterie" in message.lower() or "displej" in message.lower() or "iphone" in message.lower()

def chat_with_openai(message):
    result = ""

    # Kontext z webových stránek
    relevant_pages = find_top_matches_faiss(message, page_index, page_embeddings)
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
                f'<br><a href="{p["meta"].get("url")}" target="_blank" style="color:#0066cc">{p["meta"].get("title")}</a>'
                for p in relevant_pages if p["meta"].get("url")
            ]
            if odkazy:
                result += "<br>" + "".join(odkazy)
        except Exception as e:
            result += f"Chyba při dotazu do AI: {str(e)}"

    # Pokud dotaz je produktový nebo nic nenalezeno
    if is_product_query(message) or not result.strip():
        relevant_products = find_top_matches_faiss(message, product_index, product_embeddings)
        if relevant_products:
            relevant_items = []
            for item in relevant_products:
                meta = item["meta"]
                title = meta.get("title")
                link = meta.get("link")
                image = meta.get("{http://base.google.com/ns/1.0}image_link")
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
