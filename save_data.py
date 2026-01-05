import requests
import json
import sys
from datetime import datetime

# 1. Génère la date du jour automatiquement (ex: 2026-01-05)
date_aujourdhui = datetime.now().strftime("%Y-%m-%d")

# 2. Ton URL avec la date dynamique et le tri par heure décroissante pour avoir la dernière
URL_API = f"https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?where=date%3D%22{date_aujourdhui}%22&order_by=date_heure%20desc&limit=1"


def job():
    try:
        response = requests.get(URL_API, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            f = data["results"][0]
            
            # On ne garde que l'essentiel : Heure + Échanges
            output = [{
                "heure": f.get("heure"),
                "date": f.get("date"),
 "prevision_j1": f.get("previsions_j1", 0), # Récupération de la prévision
                
                "uk": f.get("ech_comm_angleterre", 0),
                "es": f.get("ech_comm_espagne", 0),
                "it": f.get("ech_comm_italie", 0),
                "ch": f.get("ech_comm_suisse", 0),
                "de_be": f.get("ech_comm_allemagne_belgique", 0)
            }]
            
            with open("archive_tempo.json", "w", encoding="utf-8") as file:
                json.dump(output, file, indent=4, ensure_ascii=False)
            print(f"✅ Données de {f.get('heure')} sauvegardées.")
        else:
            print("⚠️ Aucune donnée trouvée pour aujourd'hui.")
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    job()
