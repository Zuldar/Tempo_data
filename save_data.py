import requests
import json

# Nouvelle URL : Flux National Temps Réel (Données du jour uniquement)
URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=15"

def job():
    try:
        print("Interrogation du flux Temps Réel RTE...")
        response = requests.get(URL, timeout=30)
        data = response.json()
        
        # On cherche la donnée la plus récente qui a de la consommation
        valid_entry = None
        if "results" in data:
            for entry in data["results"]:
                # On vérifie que la conso est là ET que la date est bien 2026
                if entry.get("consommation") is not None and "2026" in entry.get("date_heure", ""):
                    valid_entry = entry
                    break
        
        if valid_entry:
            filename = "archive_tempo.json"
            # On écrase pour n'avoir que le point le plus récent d'aujourd'hui
            with open(filename, "w", encoding="utf-8") as f:
                json.dump([valid_entry], f, indent=4, ensure_ascii=False)
            print(f"✅ SUCCÈS : Donnée du {valid_entry['date_heure']} sauvegardée.")
        else:
            print("⚠️ ATTENTION : Aucune donnée de 2026 trouvée pour l'instant. RTE a du retard.")
            
    except Exception as e:
        print(f"❌ ERREUR : {e}")

if __name__ == "__main__":
    job()
