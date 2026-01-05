import requests
import json
import sys
from datetime import datetime

# Date automatique pour l'URL
date_aujourdhui = datetime.now().strftime("%Y-%m-%d")

# URL avec filtre Temps Réel pour éviter le bug du 23:45
URL_API = f"https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?where=date%3D%22{date_aujourdhui}%22%20and%20nature%3D%22Donn%C3%A9es%20temps%20r%C3%A9el%22&order_by=date_heure%20desc&limit=1"

def job():
    try:
        response = requests.get(URL_API, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            f = data["results"][0]
            
            # Extraction de l'heure UTC depuis le champ date_heure (ex: 2026-01-05T21:15:00+00:00)
            # On prend la partie entre 'T' et les secondes
            date_heure_full = f.get("date_heure", "")
            heure_utc = date_heure_full.split('T')[1][0:5] if 'T' in date_heure_full else f.get("heure")

            output = [{
                "heure": heure_utc, # Ici on stocke l'heure UTC (ex: 21:15 au lieu de 22:15)
                "date": f.get("date"),
                "prevision_j1": f.get("previsions_j1", 0),
                "uk": f.get("ech_comm_angleterre", 0),
                "es": f.get("ech_comm_espagne", 0),
                "it": f.get("ech_comm_italie", 0),
                "ch": f.get("ech_comm_suisse", 0),
                "de_be": f.get("ech_comm_allemagne_belgique", 0)
            }]
            
            with open("archive_tempo.json", "w", encoding="utf-8") as file:
                json.dump(output, file, indent=4, ensure_ascii=False)
            print(f"✅ Données UTC sauvegardées : {heure_utc}")
        else:
            print("⚠️ Aucune donnée trouvée.")
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    job()
