import os
import json
import requests
from bs4 import BeautifulSoup

# Seznam URL statických stránek
URLS = [
    "https://www.express-servis.cz/web/pages/vymena-baterie",
    "https://www.express-servis.cz/web/pages/vyhody-nakupu-u-nas",
    "https://www.express-servis.cz/web/pages/vse-o-nakupu",
    "https://www.express-servis.cz/web/pages/vraceni-zbozi",
    "https://www.express-servis.cz/web/pages/volne-pozice",
    "https://www.express-servis.cz/web/pages/vivoo-testovaci-prouzek",
    "https://www.express-servis.cz/web/pages/vernostni-program",
    "https://www.express-servis.cz/web/pages/vanoce-v-express-servisu",
    "https://www.express-servis.cz/web/pages/usp-slouceni-objednavek",
    "https://www.express-servis.cz/web/pages/usp-reklamace-vo",
    "https://www.express-servis.cz/web/pages/usp-podpora-a-servis",
    "https://www.express-servis.cz/web/pages/usp-doprava-vo",
    "https://www.express-servis.cz/web/pages/upgrade-mac",
    "https://www.express-servis.cz/web/pages/svoz-zarizeni",
    "https://www.express-servis.cz/web/pages/stovky-spokojenych-zakazniku",
    "https://www.express-servis.cz/web/pages/sportovni-darky",
    "https://www.express-servis.cz/web/pages/servis-telefonu-plzen",
    "https://www.express-servis.cz/web/pages/servis-tabletu-plzen",
    "https://www.express-servis.cz/web/pages/servis-konzoli",
    "https://www.express-servis.cz/web/pages/rozcestnik",
    "https://www.express-servis.cz/web/pages/repasovany-apple-zachran-planetu",
    "https://www.express-servis.cz/web/pages/reklamace-zbozi",
    "https://www.express-servis.cz/web/pages/quad-lock",
    "https://www.express-servis.cz/web/pages/pro-partnery",
    "https://www.express-servis.cz/web/pages/paf-servisni-podminky",
    "https://www.express-servis.cz/web/pages/paf-reklamace-zbozi",
    "https://www.express-servis.cz/web/pages/paf-odstoupeni-od-kupni-smlouvy",
    "https://www.express-servis.cz/web/pages/paf-obchodni-podminky-eshop",
    "https://www.express-servis.cz/web/pages/paf-gdpr-zpracovani-osobnich-udaju",
    "https://www.express-servis.cz/web/pages/paf-e-shop-dulezite-informace-k-vymene-vraceni-a-reklamaci-zbozi",
    "https://www.express-servis.cz/web/pages/paf",
    "https://www.express-servis.cz/web/pages/o-nas",
    "https://www.express-servis.cz/web/pages/novinky",
    "https://www.express-servis.cz/web/pages/modni-darky",
    "https://www.express-servis.cz/web/pages/kolobezky",
    "https://www.express-servis.cz/web/pages/jsme-specialiste-na-mobilni-prislusenstvi",
    "https://www.express-servis.cz/web/pages/jsme-odbornici-na-produkty-apple",
    "https://www.express-servis.cz/web/pages/jsme-autorizovany-prodejce-prislusenstvi",
    "https://www.express-servis.cz/web/pages/jak-vybrat-repasovany-notebook",
    "https://www.express-servis.cz/web/pages/jak-vybrat-repasovany-macbook",
    "https://www.express-servis.cz/web/pages/jak-vybrat-repasovany-iphone",
    "https://www.express-servis.cz/web/pages/jak-vybrat-repasovany-ipad",
    "https://www.express-servis.cz/web/pages/jak-vybrat-repasovane-apple-watch",
    "https://www.express-servis.cz/web/pages/chran-se-chytre",
    "https://www.express-servis.cz/web/pages/hrave-darky",
    "https://www.express-servis.cz/web/pages/hodnoceni-e-shopu-express-servis",
    "https://www.express-servis.cz/web/pages/hodnoceni-nd",
    "https://www.express-servis.cz/web/pages/express-servis-servis-iphone-plzen",
    "https://www.express-servis.cz/web/pages/darky-pro-zabavu",
    "https://www.express-servis.cz/web/pages/darky-pro-relax",
    "https://www.express-servis.cz/web/pages/darky-pro-praci",
    "https://www.express-servis.cz/web/pages/casti-displeje-iphone",
    "https://www.express-servis.cz/web/pages/cena-dopravy",
    "https://www.express-servis.cz/web/pages/b2b-express-servis-pro-firmy",
    "https://www.express-servis.cz/web/pages/apple-servis-pro-firmy",
    "https://www.express-servis.cz/kontakt-es",
    "https://www.express-servis.cz/vykup-zarizeni",
    "https://www.express-servis.cz/servis-zarizeni"
]

output = []

for url in URLS:
    try:
        print(f"Stahuji: {url}")
        html = requests.get(url, timeout=15).text
        soup = BeautifulSoup(html, "html.parser")

        # Odstranit <header>, <footer>, <nav>, případně jiné zbytečné bloky
        for tag in soup.find_all(['header', 'footer', 'nav', 'aside']):
            tag.decompose()

        # Vyhledání obsahu ve specifickém divu
        content_div = soup.find('div', id='snippet--content')

        if content_div:
            content = content_div.get_text(separator="\n", strip=True)
        else:
            content = ""  # Pokud není nalezen div, necháme prázdný obsah

        # Před uložením, filtrujeme nechtěné informace, pokud nějaké zůstávají
        filtered_content = "\n".join([line for line in content.splitlines() if line.strip() and len(line.split()) > 2])

        # Uložíme upravený obsah
        output.append({
            "url": url,
            "title": soup.title.string.strip() if soup.title else "",
            "content": filtered_content
        })
    except Exception as e:
        print(f"Chyba u {url}: {e}")

# Vytvořit složku pokud neexistuje
os.makedirs("data", exist_ok=True)

# Uložit výstup
with open("data/pages.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"Uloženo {len(output)} stránek do data/pages.json")
