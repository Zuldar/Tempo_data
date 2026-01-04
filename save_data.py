import requests
import json
import time

# URL de l'API Explore V2.1 (RTE)
TARGET_URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=10"
PROXY_URL = "https://api.allorigins.win/get?url="

def job():
    try:
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] Tentative de mise à jour...")
        
        # Encodage pour le proxy AllOrigins
        encoded_url = requests.utils.quote(TARGET_URL)
        full_url = f"{PROXY_URL}{encoded_url}&cb={int(time.time())}"
        
        response = requests.get(full_url, timeout=30)
        wrapper = response.json()
        data = json.loads(wrapper['contents'])
        
        valid_entry = None
        if "results" in data:
            # On cherche le point le plus récent qui n'est pas NULL
            for record in data["results"]:
                if record.get("consommation") is not None and record.get("nucleaire") is not None:
                    # On vérifie que c'est bien une donnée de 2026
                    if "2026" in record.get("date_heure", ""):
                        valid_entry = record
                        break
            
            if valid_entry:
                # Si on trouve une donnée 2026 valide, on écrase le fichier
                output = [{
                    "date_heure": valid_entry.get("date_heure"),
                    "heure": valid_entry.get("heure"),
                    "consommation": valid_entry.get("consommation"),
                    "nucleaire": valid_entry.get("nucleaire"),
                    "eolien": valid_entry.get("eolien"),
                    "solaire": valid_entry.get("solaire"),
                    "hydraulique": valid_entry.get("hydraulique"),
                    "gaz": valid_entry.get("gaz"),
                    "ech_comm_angleterre": valid_entry.get("ech_comm_angleterre"),
                    "ech_comm_espagne": valid_entry.get("ech_comm_espagne"),
                    "ech_comm_italie": valid_entry.get("ech_comm_italie"),
                    "ech_comm_suisse": valid_entry.get("ech_comm_suisse"),
                    "ech_comm_allemagne_belgique": valid_entry.get("ech_comm_allemagne_belgique"),
                    "ech_comm_belgique": valid_entry.get("ech_comm_belgique")
                }]
                
                with open("archive_tempo.json", "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=4, ensure_ascii=False)
                print(f"✅ SUCCÈS : Nouvelle donnée 2026 enregistrée ({valid_entry['heure']}).")
            else:
                # SI AUCUNE DONNÉE 2026 VALIDE : ON NE FAIT RIEN
                # Le fichier 'archive_tempo.json' sur GitHub reste tel quel (données du 31/12)
                print("⚠️ RTE renvoie des données vides ou anciennes. Conservation de l'archive existante.")
        
    except Exception as e:
        print(f"💥 Erreur : {e}. Le fichier actuel n'a pas été modifié.")

if __name__ == "__main__":
    job()
