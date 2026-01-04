import requests
import json
import time

# On demande les 10 derniers records pour être sûr d'en trouver un rempli
TARGET_URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=10"
PROXY_URL = "https://api.allorigins.win/get?url="

def job():
    try:
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] Recherche du dernier point valide (non null)...")
        
        encoded_url = requests.utils.quote(TARGET_URL)
        full_url = f"{PROXY_URL}{encoded_url}&cb={int(time.time())}"
        
        response = requests.get(full_url, timeout=30)
        wrapper = response.json()
        data = json.loads(wrapper['contents'])
        
        valid_entry = None
        
        if "results" in data:
            # On parcourt les 10 points en partant du plus récent
            for record in data["results"]:
                # Condition : la consommation doit être un nombre (pas None/null)
                if record.get("consommation") is not None:
                    valid_entry = record
                    break # On a trouvé le plus récent rempli, on s'arrête
            
            if valid_entry:
                output = [{
                    "date_heure": valid_entry.get("date_heure"),
                    "heure": valid_entry.get("heure"),
                    "consommation": valid_entry.get("consommation", 0),
                    "nucleaire": valid_entry.get("nucleaire", 0),
                    "eolien": valid_entry.get("eolien", 0),
                    "solaire": valid_entry.get("solaire", 0),
                    "hydraulique": valid_entry.get("hydraulique", 0),
                    "gaz": valid_entry.get("gaz", 0),
                    "bioenergies": valid_entry.get("bioenergies", 0),
                    "ech_comm_angleterre": valid_entry.get("ech_comm_angleterre", 0),
                    "ech_comm_espagne": valid_entry.get("ech_comm_espagne", 0),
                    "ech_comm_italie": valid_entry.get("ech_comm_italie", 0),
                    "ech_comm_suisse": valid_entry.get("ech_comm_suisse", 0),
                    "ech_comm_allemagne_belgique": valid_entry.get("ech_comm_allemagne_belgique", 0),
                    "ech_comm_belgique": valid_entry.get("ech_comm_belgique", 0)
                }]
                
                with open("archive_tempo.json", "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=4, ensure_ascii=False)
                print(f"✅ SUCCÈS : Point valide trouvé à {valid_entry['heure']} ({valid_entry['consommation']} MW).")
            else:
                print("⚠️ Aucun des 10 derniers points ne contient de données. RTE est en cours de mise à jour.")
        else:
            print("❌ Structure JSON vide ou erronée.")
                
    except Exception as e:
        print(f"💥 Erreur : {e}")

if __name__ == "__main__":
    job()
