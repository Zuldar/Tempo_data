import requests
import json
import sys
from datetime import datetime

# 1. Configuration dynamique de la date
date_aujourdhui = datetime.now().strftime("%Y-%m-%d")

# 2. URL cible : on demande 96 points (24h) pour garantir la présence de la prévision
URL_API = f"https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?where=date%3D%22{date_aujourdhui}%22&order_by=date_heure%20desc&limit=96"

def job():
    try:
        response = requests.get(URL_API, timeout=15)
        response.raise_for_status()
        data = response.json()
        results = data.get("results", [])
        
        if len(results) > 0:
            # On prend l'heure et les flux sur le point le plus récent (Index 0)
            flux_recent = results[0]
            
            # Initialisation de la prévision
            prev_val = 0
            
            # Boucle de recherche : on parcourt les 96 points pour trouver la prévision J+1
            for record in results:
                # L'API peut utiliser 'previsions_j1' ou 'consommation_prevue'
                v = record.get("previsions_j1") or record.get("consommation_prevue") or 0
                if v > 0:
                    prev_val = v
                    break # On a trouvé la valeur, on arrête de chercher
            
            # Construction du fichier JSON final
            output = [{
                "heure": flux_recent.get("heure"),
                "date": flux_recent.get("date"),
                "prevision_j1": prev_val,
                "uk": flux_recent.get("ech_comm_angleterre", 0),
                "es": flux_recent.get("ech_comm_espagne", 0),
                "it": flux_recent.get("ech_comm_italie", 0),
                "ch": flux_recent.get("ech_comm_suisse", 0),
                "de_be": flux_recent.get("ech_comm_allemagne_belgique", 0)
            }]
            
            # Sauvegarde locale
            with open("archive_tempo.json", "w", encoding="utf-8") as f:
                json.dump(output, f, indent=4, ensure_ascii=False)
            
            print(f"✅ Succès ! Heure: {flux_recent.get('heure')} | Prévision J+1: {prev_val} MW")
        else:
            print(f"⚠️ Aucune donnée trouvée pour aujourd'hui ({date_aujourdhui}).")
            
    except Exception as e:
        print(f"❌ Erreur critique : {e}")
        sys.exit(1)

if __name__ == "__main__":
    job()
