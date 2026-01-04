import requests
import json

# API v2.1 : on demande les 10 derniers pour être sûr d'avoir une ligne remplie
URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=10"

def job():
    try:
        response = requests.get(URL)
        data = response.json()
        
        if "results" in data:
            # On cherche dans les 10 derniers la première ligne qui a de la consommation
            # Cela permet d'éviter les lignes "null" que tu as reçues
            valid_entry = None
            for entry in data["results"]:
                if entry.get("consommation") is not None:
                    valid_entry = entry
                    break
            
            if valid_entry:
                filename = "archive_tempo.json"
                
                # On crée une liste avec UNIQUEMENT la donnée du jour (écrase l'ancien)
                history = [valid_entry]
                
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(history, f, indent=4, ensure_ascii=False)
                
                print(f"Succès : Fichier remplacé par la donnée valide du {valid_entry['date_heure']}")
            else:
                print("Aucune donnée valide (non nulle) trouvée dans les derniers relevés.")
                
    except Exception as e:
        print(f"Erreur lors de la capture : {e}")

if __name__ == "__main__":
    job()
