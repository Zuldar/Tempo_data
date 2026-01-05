import requests
import json
import time
import os

# Configuration de l'URL cible (Données du 5 Janvier 2026)
URL_API = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?where=date%3D%222026-01-05%22&order_by=date_heure%20desc&limit=1"

def job():
    try:
        print(f"[{time.strftime('%H:%M:%S')}] Tentative de téléchargement des données...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json'
        }
        
        response = requests.get(URL_API, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Erreur serveur RTE : {response.status_code}")
            return

        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            f = data["results"][0]
            
            # On prépare l'objet JSON pour la console HTML
            output = [{
                "date": f.get("date"),
                "heure": f.get("heure"),
                "date_heure": f.get("date_heure"),
                "consommation": f.get("consommation"),
                "nucleaire": f.get("nucleaire"),
                "eolien": f.get("eolien"),
                "solaire": f.get("solaire"),
                "hydraulique": f.get("hydraulique"),
                "gaz": f.get("gaz"),
                # Récupération des échanges commerciaux
                "ech_comm_angleterre": f.get("ech_comm_angleterre", 0),
                "ech_comm_espagne": f.get("ech_comm_espagne", 0),
                "ech_comm_italie": f.get("ech_comm_italie", 0),
                "ech_comm_suisse": f.get("ech_comm_suisse", 0),
                "ech_comm_allemagne_belgique": f.get("ech_comm_allemagne_belgique", 0)
            }]
            
            # Sauvegarde locale du fichier
            with open("archive_tempo.json", "w", encoding="utf-8") as file:
                json.dump(output, file, indent=4, ensure_ascii=False)
            
            print(f"✅ SUCCÈS : Données de {f.get('heure')} enregistrées.")
        else:
            print("⚠️ L'API a répondu mais le résultat est vide pour 2026.")

    except Exception as e:
        print(f"💥 Erreur critique : {e}")

if __name__ == "__main__":
    # Boucle pour s'exécuter toutes les heures (3600 secondes)
    while True:
        job()
        print("😴 Sommeil pour 1 heure...")
        time.sleep(3600)
