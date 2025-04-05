# generate_embeddings.py
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_embedding(text):
    try:
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text.replace("\n", " ")
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Chyba při generování embeddingu: {e}")
        return []


def embed_and_save(input_file, output_file, text_fields):
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    embedded_data = []
    for item in tqdm(data if isinstance(data, list) else data.values()):
        try:
            content = " ".join(str(item.get(field, "")) for field in text_fields).strip()
            embedding = get_embedding(content)
            embedded_data.append({
                "embedding": embedding,
                "content": content,
                "meta": item  # uložíme původní data
            })
        except Exception as e:
            print(f"Chyba při zpracování položky: {e}")
            continue

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(embedded_data, f, ensure_ascii=False, indent=2)

    print(f"Uloženo do {output_file}")


if __name__ == "__main__":
    embed_and_save("data/products.json", "data/products_embeddings.json", ["title", "description"])
    embed_and_save("data/pages.json", "data/pages_embeddings.json", ["title", "content"])
