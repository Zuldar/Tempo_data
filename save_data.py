import requests
import json
import time

# URL directe ODRE (sans le wrapper AllOrigins qui sature)
URL_API = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=20"

def job():
    try:
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] Connexion directe API ODRE...")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json'
        }

        # On interroge directement l'API
        response = requests.get(URL_API, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Erreur Serveur : {response.status_code}")
            return

        data = response.json()
        
        valid_entry = None
        if "results" in data:
            for record in data["results"]:
                # On cherche le point le plus récent qui a de la consommation
                if record.get("consommation") is not None:
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
                print(f"✅ SUCCÈS : Données du {valid_entry.get('date_heure')} sauvegardées.")
            else:
                print("⚠️ Aucun résultat valide trouvé dans le flux.")
                
    except Exception as e:
        print(f"💥 Échec critique : {e}")

if __name__ == "__main__":
    job()
