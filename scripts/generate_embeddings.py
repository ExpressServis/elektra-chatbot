import os
import sys
import json
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

# Přidání cesty k rootu projektu, aby šel importovat faiss_utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from faiss_utils import create_faiss_index, save_index

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY není nastaven v prostředí.")

client = OpenAI(api_key=api_key)

def get_embedding(text):
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text.replace("\n", " ")
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Chyba při generování embeddingu: {e}")
        return []

def validate_embeddings(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                if not item.get("embedding") or len(item["embedding"]) != 1536:
                    print(f"⚠️ Nevalidní embedding v souboru {file_path}.")
                    return False
        print(f"✅ Validace embeddingu úspěšná: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Chyba při validaci {file_path}: {e}")
        return False

def embed_and_save(input_file, output_json_file, index_output_file, text_fields):
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Nelze načíst {input_file}: {e}")
        return

    embedded_data = []
    vectors = []
    for item in tqdm(data if isinstance(data, list) else data.values(), desc=f"Generuji embeddingy pro {input_file}"):
        try:
            content = " ".join(str(item.get(field, "")) for field in text_fields).strip()
            embedding = get_embedding(content)
            if embedding:
                embedded_data.append({
                    "embedding": embedding,
                    "content": content,
                    "meta": item
                })
                vectors.append(embedding)
        except Exception as e:
            print(f"⚠️ Chyba při zpracování položky: {e}")
            continue

    try:
        with open(output_json_file, "w", encoding="utf-8") as f:
            json.dump(embedded_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Uloženo do {output_json_file}")
    except Exception as e:
        print(f"❌ Nelze uložit do {output_json_file}: {e}")

    validate_embeddings(output_json_file)

    # Uložení Faiss indexu
    try:
        vectors_np = np.array(vectors, dtype=np.float32)
        index = create_faiss_index(vectors_np)
        save_index(index, index_output_file)
        print(f"✅ Faiss index uložen do {index_output_file}")
    except Exception as e:
        print(f"❌ Chyba při ukládání Faiss indexu: {e}")

if __name__ == "__main__":
    embed_and_save(
        "data/products.json",
        "data/products_embeddings.json",
        "data/faiss_product_index.bin",
        ["title", "description"]
    )
    embed_and_save(
        "data/pages.json",
        "data/pages_embeddings.json",
        "data/faiss_page_index.bin",
        ["title", "content"]
    )
