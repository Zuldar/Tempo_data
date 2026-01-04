import requests
import json
import time

# On augmente la limite à 50 records pour remonter plus loin dans le temps si besoin
TARGET_URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=50"
PROXY_URL = "https://api.allorigins.win/get?url="

def job():
    try:
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] Recherche profonde (50 derniers points)...")
        
        encoded_url = requests.utils.quote(TARGET_URL)
        full_url = f"{PROXY_URL}{encoded_url}&cb={int(time.time())}"
        
        response = requests.get(full_url, timeout=30)
        wrapper = response.json()
        data = json.loads(wrapper['contents'])
        
        valid_entry = None
        
        if "results" in data:
            for record in data["results"]:
                # On cherche le PREMIER point qui a une valeur NUCLEAIRE (le plus fiable)
                if record.get("nucleaire") is not None and record.get("nucleaire") > 0:
                    valid_entry = record
                    break
            
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
                print(f"✅ SUCCÈS : Donnée trouvée à {valid_entry['date_heure']} ({valid_entry['nucleaire']} MW Nuc).")
            else:
                print("⚠️ Toujours aucune donnée réelle. Le flux RTE 2026 est encore vide (Maintenance probable).")
        else:
            print("❌ Problème de réception JSON.")
                
    except Exception as e:
        print(f"💥 Erreur : {e}")

if __name__ == "__main__":
    job()
