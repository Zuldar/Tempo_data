import requests
import json
import sys

# URL directe pour le 5 janvier 2026
URL_API = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?where=date%3D%222026-01-05%22&order_by=date_heure%20desc&limit=1"

def job():
    try:
        # On limite l'attente à 10 secondes
        response = requests.get(URL_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and len(data["results"]) > 0:
            f = data["results"][0]
            output = [{
                "date": f.get("date"),
                "heure": f.get("heure"),
                "date_heure": f.get("date_heure"),
                "consommation": f.get("consommation"),
                "nucleaire": f.get("nucleaire"),
                "eolien": f.get("eolien"),
                "solaire": f.get("solaire"),
                "hydraulique": f.get("hydraulique"),
                "gaz": f.get("gaz"),
                "ech_comm_angleterre": f.get("ech_comm_angleterre", 0),
                "ech_comm_espagne": f.get("ech_comm_espagne", 0),
                "ech_comm_italie": f.get("ech_comm_italie", 0),
                "ech_comm_suisse": f.get("ech_comm_suisse", 0),
                "ech_comm_allemagne_belgique": f.get("ech_comm_allemagne_belgique", 0)
            }]
            
            with open("archive_tempo.json", "w", encoding="utf-8") as file:
                json.dump(output, file, indent=4, ensure_ascii=False)
            print("✅ Sauvegarde terminée avec succès.")
        else:
            print("⚠️ Aucune donnée trouvée.")
            
    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    job()
