import requests
import json
import os

URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=20"

def job():
    try:
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()
        
        valid_entry = None
        if "results" in data:
            for entry in data["results"]:
                # On vérifie que la consommation est présente et réelle
                if entry.get("consommation") is not None and entry.get("consommation") > 0:
                    valid_entry = entry
                    break
            
            if valid_entry:
                filename = "archive_tempo.json"
                # On force l'écrasement avec la donnée fraîche
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump([valid_entry], f, indent=4, ensure_ascii=False)
                print(f"✅ Fichier mis à jour avec succès ({valid_entry['date_heure']})")
    except Exception as e:
        print(f"❌ Erreur : {e}")

if __name__ == "__main__":
    job()
