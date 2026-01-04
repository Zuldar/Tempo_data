import requests
import json
import time

# On utilise l'URL la plus simple et robuste
URL = "https://odre.opendatasoft.com/api/records/1.0/search/?dataset=eco2mix-national-tr&rows=1&sort=-date_heure"

def job():
    try:
        print(f"Tentative de connexion à {time.strftime('%H:%M:%S')}...")
        response = requests.get(URL, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if "records" in data and len(data["records"]) > 0:
                fields = data["records"][0]["fields"]
                date_heure = fields.get("date_heure", "")
                
                print(f"Donnée reçue du serveur : {date_heure}")

                # CONDITION DE SÉCURITÉ : On n'enregistre que si c'est 2026
                if "2026" in date_heure:
                    with open("archive_tempo.json", "w", encoding="utf-8") as f:
                        json.dump([fields], f, indent=4, ensure_ascii=False)
                    print("✅ RÉUSSITE : Le fichier archive_tempo.json a été mis à jour avec 2026 !")
                else:
                    print("❌ ÉCHEC : Le serveur RTE renvoie encore des archives de 2024.")
            else:
                print("⚠️ Serveur répond mais aucun enregistrement trouvé.")
        else:
            print(f"⚠️ Erreur serveur RTE : {response.status_code}")

    except Exception as e:
        print(f"💥 Erreur de connexion (Timeout) : {e}")

if __name__ == "__main__":
    job()
