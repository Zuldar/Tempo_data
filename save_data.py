import requests
import json
import os

# L'adresse où on récupère les données
URL = "https://odre.opendatasoft.com/api/records/1.0/search/?dataset=eco2mix-national-tr&rows=1&sort=-date_heure"

def capturer():
    # 1. On demande les données à RTE
    reponse = requests.get(URL)
    donnees = reponse.json()
    
    # 2. On extrait la ligne qui nous intéresse
    info = donnees["records"][0]["fields"]
    
    # 3. On prépare notre fichier d'archive
    nom_fichier = "archive_tempo.json"
    
    if os.path.exists(nom_fichier):
        with open(nom_fichier, "r") as f:
            historique = json.load(f)
    else:
        historique = []
    
    # 4. On ajoute la donnée si elle est nouvelle
    historique.append(info)
    
    # 5. On enregistre le fichier
    with open(nom_fichier, "w") as f:
        json.dump(historique, f, indent=4)

if __name__ == "__main__":
    capturer()
