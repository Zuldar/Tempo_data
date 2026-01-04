import requests
import json
import os

# URL optimisée pour le 4 janvier 2026
URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=1"

def job():
    try:
        response = requests.get(URL)
        data = response.json()
        
        # Dans l'API v2.1, les données sont dans "results"
        if "results" in data and len(data["results"]) > 0:
            entry = data["results"][0]
            filename = "archive_tempo.json"
            
            # Charger l'historique
            if os.path.exists(filename):
                with open(filename, "r", encoding="utf-8") as f:
                    history = json.load(f)
            else:
                history = []
            
            # Vérifier si c'est une nouvelle donnée (comparaison date_heure)
            if not any(item.get("date_heure") == entry["date_heure"] for item in history):
                history.append(entry)
                # On ne garde que les 100 dernières pour ne pas alourdir le fichier
                history = history[-100:] 
                
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(history, f, indent=4, ensure_ascii=False)
                print(f"Succès : Donnée du {entry['date_heure']} ajoutée.")
            else:
                print("Donnée déjà archivée.")
    except Exception as e:
        print(f"Erreur : {e}")

if __name__ == "__main__":
    job()
