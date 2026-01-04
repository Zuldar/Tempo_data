import requests
import json
import os

URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=20"

def job():
    try:
        print("1. Tentative de connexion à RTE...")
        response = requests.get(URL, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        print(f"2. Réponse reçue. Nombre de résultats : {len(data.get('results', []))}")
        
        valid_entry = None
        if "results" in data:
            for entry in data["results"]:
                conso = entry.get("consommation")
                # On accepte la donnée si conso est un nombre > 0
                if conso is not None and conso > 0:
                    valid_entry = entry
                    print(f"3. Donnée valide trouvée pour : {entry.get('date_heure')} (Conso: {conso})")
                    break
            
            if valid_entry:
                filename = "archive_tempo.json"
                # On écrase tout avec la nouvelle liste
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump([valid_entry], f, indent=4, ensure_ascii=False)
                print(f"4. Fichier '{filename}' écrit localement sur le serveur GitHub.")
            else:
                print("3. Erreur : Aucune ligne avec consommation > 0 trouvée dans les 20 derniers relevés.")
    except Exception as e:
        print(f"ERREUR : {e}")

if __name__ == "__main__":
    job()
