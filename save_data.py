import requests
import json
import sys

# On repasse sur l'URL classique search qui est parfois plus réactive
URL = "https://odre.opendatasoft.com/api/records/1.0/search/?dataset=eco2mix-national-tr&rows=10&sort=-date_heure"

def job():
    try:
        print("--- DEBUT DU DIAGNOSTIC ---")
        response = requests.get(URL, timeout=30)
        data = response.json()
        
        # On affiche ce qu'on reçoit pour débugger
        if "records" not in data:
            print("ERREUR: 'records' absent du JSON. Voici le JSON reçu :")
            print(data)
            return

        records = data["records"]
        print(f"Nombre de lignes reçues : {len(records)}")

        valid_entry = None
        for r in records:
            f = r["fields"]
            conso = f.get("consommation")
            print(f"Vérification ligne {f.get('date_heure')} : Conso = {conso}")
            
            if conso is not None and conso > 0:
                valid_entry = f
                break

        if valid_entry:
            print(f"SUCCÈS: Donnée trouvée pour {valid_entry['date_heure']}")
            with open("archive_tempo.json", "w", encoding="utf-8") as file:
                json.dump([valid_entry], file, indent=4, ensure_ascii=False)
            print("Fichier écrit sur le disque du serveur.")
        else:
            print("ERREUR: Aucune donnée avec conso > 0 trouvée.")
            
    except Exception as e:
        print(f"ERREUR CRITIQUE: {e}")

if __name__ == "__main__":
    job()
