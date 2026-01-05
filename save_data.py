import requests
import json
import time

# On utilise ton URL qui fonctionne bien
TARGET_URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=20"
PROXY_URL = "https://api.allorigins.win/get?url="

def job():
    try:
        print(f"[{time.strftime('%H:%M:%S')}] Scan des 20 derniers records RTE...")
        
        encoded_url = requests.utils.quote(TARGET_URL)
        full_url = f"{PROXY_URL}{encoded_url}&cb={int(time.time())}"
        
        response = requests.get(full_url, timeout=30)
        wrapper = response.json()
        data = json.loads(wrapper['contents'])
        
        valid_entry = None
        if "results" in data:
            for record in data["results"]:
                # Condition stricte : il faut de la conso ET du nucléaire pour valider
                if record.get("consommation") is not None and record.get("nucleaire") is not None:
                    valid_entry = record
                    break # On a trouvé le point réel le plus récent, on sort !
            
            if valid_entry:
                output = [{
                    "date_heure": valid_entry.get("date_heure"),
                    "heure": valid_entry.get("heure"),
                    "consommation": valid_entry.get("consommation"),
                    "nucleaire": valid_entry.get("nucleaire"),
                    "eolien": valid_entry.get("eolien"),
                    "solaire": valid_entry.get("solaire"),
                    "hydraulique": valid_entry.get("hydraulique"),
                    "gaz": valid_entry.get("gaz"),
                    "bioenergies": valid_entry.get("bioenergies"),
                    "ech_comm_angleterre": valid_entry.get("ech_comm_angleterre", 0),
                    "ech_comm_espagne": valid_entry.get("ech_comm_espagne", 0),
                    "ech_comm_italie": valid_entry.get("ech_comm_italie", 0),
                    "ech_comm_suisse": valid_entry.get("ech_comm_suisse", 0),
                    "ech_comm_allemagne_belgique": valid_entry.get("ech_comm_allemagne_belgique", 0),
                    "ech_comm_belgique": valid_entry.get("ech_comm_belgique", 0)
                }]
                
                with open("archive_tempo.json", "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=4, ensure_ascii=False)
                print(f"✅ SUCCÈS : Donnée du {valid_entry.get('date_heure')} capturée !")
            else:
                print("⚠️ Les 20 records sont vides. RTE n'a pas encore rempli les colonnes.")
        
    except Exception as e:
        print(f"💥 Erreur : {e}")

if __name__ == "__main__":
    job()
