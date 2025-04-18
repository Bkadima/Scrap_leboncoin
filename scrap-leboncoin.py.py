import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import csv
import time

ua = UserAgent()
headers = {'User-Agent': ua.random}

def get_liens_annonces(page=1):
    url = f"https://www.leboncoin.fr/recherche?category=2&manufacturer=renault&page={page}"
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        print(f"[ERREUR PAGE {page}] Code:", response.status_code)
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    cartes = soup.find_all('a', class_='styles_adCard__2YFTi')
    liens = ["https://www.leboncoin.fr" + carte.get('href') for carte in cartes]
    return liens

def extraire_infos_annonce(url):
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, 'html.parser')

    # Titre
    titre_tag = soup.find('h1')
    titre = titre_tag.text.strip() if titre_tag else "N/A"

    # Prix
    prix_tag = soup.find('div', class_='styles_price__xS4Qu')
    prix = prix_tag.text.strip() if prix_tag else "N/A"

    details = {
    'Modèle': titre,
    'Prix': prix,
    'Kilométrage': "N/A",
    'Année': "N/A",
    'Moteur': "N/A",
    'Boîte': "N/A",
    'Carburant': "N/A",
    'Lien': url
    }

    infos = soup.find_all('div', class_='styles_item__3Z2R3')

    for info in infos:
        label = info.find('p', class_='styles_label__29PH_')
        value = info.find('p', class_='styles_value__uGzEr')

        if label and value:
            label = label.text.strip().lower()
            value = value.strip()

            if 'kilométrage' in label:
                details['Kilométrage'] = value
            elif 'mise en circulation' in label or 'année' in label:
                details['Année'] = value
            elif 'boîte' in label:
                details['Boîte'] = value
            elif 'carburant' in label:
                details['Carburant'] = value
            elif 'motorisation' in label:
                details['Moteur'] = value

    return details

# --- Scraping ---
annonces_total = []
for page in range(1, 100): # Tu peux augmenter à 10 ou plus
    print(f"Scraping page {page}...")
    urls = get_liens_annonces(page)
    for lien in urls:
        infos = extraire_infos_annonce(lien)
        if infos:
            annonces_total.append(infos)
            print(f"> {infos['Modèle']} | {infos['Prix']}")
        time.sleep(0.5)

# --- Export CSV ---
with open('renault_leboncoin.csv', 'w', newline='', encoding='utf-8') as fichier_csv:
    champs = ['Modèle', 'Prix', 'Kilométrage', 'Année', 'Moteur', 'Boîte', 'Carburant', 'Lien']
    writer = csv.DictWriter(fichier_csv, fieldnames=champs)
    writer.writeheader()
    writer.writerows(annonces_total)

print(f"\n--- {len(annonces_total)} annonces enregistrées dans 'renault_leboncoin.csv' ---")