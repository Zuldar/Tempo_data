import requests
import json
import time

# URL avec filtre strict sur l'année 2026 + Anti-cache
timestamp = int(time.time())
URL = (
    "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records"
    "?where=date_heure%20like%20%222026%2A%22" # Filtre : commence par 2026
    "&order_by=date_heure%20desc"
    "&limit=5"
    f"&cb={timestamp}"
)

def job():
    try:
        print(f"Appel API RTE (Filtre 2026) à {time.strftime('%H:%M:%S')}")
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        valid_entry = None
        if "results" in data and len(data["results"]) > 0:
            for entry in data["results"]:
                # On vérifie que la consommation est présente
                if entry.get("consommation") is not None:
                    valid_entry = entry
                    break
            
            if valid_entry:
                filename = "archive_tempo.json"
                # On écrase TOUT le fichier avec la donnée de 2026
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump([valid_entry], f, indent=4, ensure_ascii=False)
                print(f"✅ TROUVÉ : {valid_entry['date_heure']} - Enregistré.")
            else:
                print("⚠️ RTE répond mais aucune ligne n'a de consommation remplie pour 2026.")
        else:
            print("❌ Aucun résultat pour 2026 dans la base RTE actuellement.")
                
    except Exception as e:
        print(f"💥 Erreur : {e}")

if __name__ == "__main__":
    job()
