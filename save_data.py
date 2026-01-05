import requests
import json
import sys
from datetime import datetime

date_aujourdhui = datetime.now().strftime("%Y-%m-%d")

# On demande 96 points pour scanner toute la journée
URL_API = f"https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?where=date%3D%22{date_aujourdhui}%22&order_by=date_heure%20desc&limit=96"

def job():
    try:
        response = requests.get(URL_API, timeout=15)
        response.raise_for_status()
        results = response.json().get("results", [])
        
        if len(results) > 0:
            # Flux et Heure sur le point le plus récent
            f = results[0]
            
            prev_val = 0
            # On parcourt les lignes pour trouver LA prévision
            for r in results:
                # On teste TOUS les noms de champs connus chez RTE pour la prévision
                # 1. previsions_j1 (le plus fréquent dans eco2mix)
                # 2. consommation_prevue (parfois utilisé)
                # 3. prev_cons (rare)
                v = r.get("previsions_j1") or r.get("consommation_prevue") or r.get("prev_cons") or 0
                
                if v > 0:
                    prev_val = v
                    break
            
            output = [{
                "heure": f.get("heure"),
                "date": f.get("date"),
                "prevision_j1": prev_val,
                "uk": f.get("ech_comm_angleterre", 0),
                "es": f.get("ech_comm_espagne", 0),
                "it": f.get("ech_comm_italie", 0),
                "ch": f.get("ech_comm_suisse", 0),
                "de_be": f.get("ech_comm_allemagne_belgique", 0)
            }]
            
            with open("archive_tempo.json", "w", encoding="utf-8") as file:
                json.dump(output, file, indent=4, ensure_ascii=False)
            
            print(f"✅ Heure: {f.get('heure')} | Prévision J+1: {prev_val} MW")
        else:
            print("⚠️ Pas de données.")
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    job()
