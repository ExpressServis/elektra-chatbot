import os
import json
import requests
import xml.etree.ElementTree as ET

# Definuj URL feedů
FEED_URLS = {
    "google": "https://api.express-servis.cz/files/shop/feeds/google",
    "heureka": "https://api.express-servis.cz/files/shop/feeds/heureka",
    "zbozi": "https://api.express-servis.cz/files/shop/feeds/zbozi"
}

def parse_feed(url):
    response = requests.get(url)
    root = ET.fromstring(response.content)
    products = {}

    # Google feed – namespace
    namespaces = {'g': 'http://base.google.com/ns/1.0'}

    for item in root.findall(".//item"):
        # Google
        ean = item.findtext("g:gtin", default=None, namespaces=namespaces)
        product_no = item.findtext("g:mpn", default=None, namespaces=namespaces)

        # Heureka a Zbozi.cz
        if not ean:
            ean = item.findtext("EAN")
        if not product_no:
            product_no = item.findtext("PRODUCTNO")

        # fallback (např. ITEM_ID)
        if not product_no:
            product_no = item.findtext("ITEM_ID")

        key = ean or product_no
        if not key:
            continue

        product_data = {child.tag: child.text for child in item}
        products[key] = product_data

    return products

def merge_feeds(feeds_data):
    """
    Spojí data ze všech feedů.
    Pokud se ve více feedech objeví produkt se stejným klíčem,
    informace se sloučí (data z pozdějších feedů přepíšou ta předchozí).
    """
    merged = {}
    for feed_name, data in feeds_data.items():
        for key, product in data.items():
            if key in merged:
                merged[key].update(product)
            else:
                merged[key] = product
    return merged

def update_products_json():
    feeds_data = {}
    for name, url in FEED_URLS.items():
        print(f"Stahuji feed: {name}")
        try:
            feeds_data[name] = parse_feed(url)
        except Exception as e:
            print(f"Chyba při stahování nebo zpracování feedu {name}: {e}")
            feeds_data[name] = {}
    
    merged_products = merge_feeds(feeds_data)
    
    # Uložení výsledného JSON do adresáře "data"
    output_dir = "data"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "products.json")
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(merged_products, f, ensure_ascii=False, indent=2)
    
    print(f"Uloženo {len(merged_products)} produktů do {output_file}")

if __name__ == "__main__":
    update_products_json()
