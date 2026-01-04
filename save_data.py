import requests
import json
import os

# On demande les 20 derniers relevés pour avoir une marge de sécurité
URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=20"

def job():
    try:
        print("Interrogation de l'API RTE...")
        response = requests.get(URL)
        response.raise_for_status()
        data = response.json()
        
        valid_entry = None
        
        if "results" in data:
            # On boucle sur les résultats du plus récent au plus ancien
            for entry in data["results"]:
                # CONDITION DOUBLE : La conso doit exister ET être supérieure à 0
                conso = entry.get("consommation")
                if conso is not None and conso > 0:
                    valid_entry = entry
                    print(f"Donnée valide trouvée pour {entry.get('date_heure')}")
                    break # On a trouvé la plus récente qui est remplie, on s'arrête.
            
            if valid_entry:
                filename = "archive_tempo.json"
                
                # On crée une liste avec cette unique donnée (écrase l'historique)
                data_to_save = [valid_entry]
                
                # Écriture propre du fichier
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data_to_save, f, indent=4, ensure_ascii=False)
                
                print(f"Fichier {filename} mis à jour avec succès.")
            else:
                print("Alerte : Aucune ligne avec une consommation valide n'a été trouvée.")
        else:
            print("Erreur : Structure JSON inattendue.")
                
    except Exception as e:
        print(f"Erreur lors de l'exécution : {e}")

if __name__ == "__main__":
    job()
