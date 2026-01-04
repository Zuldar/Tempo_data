import requests
import json
import time

# URL simplifiée avec filtre 'refine' sur l'année 2026
timestamp = int(time.time())
URL = (
    "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records"
    "?order_by=date_heure%20desc"
    "&limit=10"
    "&refine=date%3A2026"  # Filtre proprement sur l'année 2026
    f"&cb={timestamp}"
)

def job():
    try:
        print(f"Appel API RTE à {time.strftime('%H:%M:%S')}")
        response = requests.get(URL, timeout=30)
        
        # Si l'API renvoie une erreur, on l'affiche précisément
        if response.status_code != 200:
            print(f"❌ Erreur API : {response.status_code}")
            print(response.text)
            return

        data = response.json()
        
        valid_entry = None
        if "results" in data and len(data["results"]) > 0:
            for entry in data["results"]:
                # On s'assure qu'il y a de la consommation
                if entry.get("consommation") is not None:
                    valid_entry = entry
                    break
            
            if valid_entry:
                filename = "archive_tempo.json"
                # On écrit le fichier (écrase tout)
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump([valid_entry], f, indent=4, ensure_ascii=False)
                print(f"✅ TROUVÉ : {valid_entry['date_heure']}")
            else:
                print("⚠️ Aucune donnée avec consommation trouvée pour 2026.")
        else:
            print("❌ Aucun résultat reçu pour 2026.")
                
    except Exception as e:
        print(f"💥 Erreur script : {e}")

if __name__ == "__main__":
    job()
