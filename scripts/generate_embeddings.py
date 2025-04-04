import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# Bezpečně načteme klíč z prostředí a ověříme
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY není nastaven v prostředí. Přidejte jej do GitHub Secrets nebo .env souboru.")

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
            if not data:
                print(f"⚠️ Soubor {file_path} je prázdný nebo neobsahuje žádné položky.")
                return False
            for item in data:
                if not item.get("embedding") or len(item["embedding"]) != 1536:
                    print(f"⚠️ Nevalidní embedding v souboru {file_path}.")
                    return False
        print(f"✅ Validace embeddingu úspěšná: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Chyba při validaci {file_path}: {e}")
        return False

def embed_and_save(input_file, output_file, text_fields):
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Nelze načíst {input_file}: {e}")
        return

    embedded_data = []
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
        except Exception as e:
            print(f"⚠️ Chyba při zpracování položky: {e}")
            continue

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(embedded_data, f, ensure_ascii=False, indent=2)
        print(f"✅ Uloženo do {output_file}")
    except Exception as e:
        print(f"❌ Nelze uložit do {output_file}: {e}")

    validate_embeddings(output_file)

if __name__ == "__main__":
    embed_and_save("data/products.json", "data/products_embeddings.json", ["title", "description"])
    embed_and_save("data/pages.json", "data/pages_embeddings.json", ["title", "content"])
