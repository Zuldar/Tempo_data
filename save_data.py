import requests
import json
import time

# On change de source : Flux direct Eco2mix (plus robuste que le portail OpenData)
URL = "https://www.rte-france.com/eco2mix/null" # Ce flux est souvent plus stable en direct

def job():
    try:
        # On tente une URL alternative simplifiée pour éviter le Timeout
        # Si ODRE ne répond pas, on utilise l'API de recherche rapide
        fallback_url = "https://odre.opendatasoft.com/api/records/1.0/search/?dataset=eco2mix-national-tr&rows=1&sort=-date_heure"
        
        print(f"Tentative de connexion à RTE à {time.strftime('%H:%M:%S')}...")
        
        # On réduit le timeout à 10s pour ne pas attendre dans le vide
        response = requests.get(fallback_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if "records" in data and len(data["records"]) > 0:
                fields = data["records"][0]["fields"]
                
                # Vérification de l'année 2026
                if "2026" in fields.get("date_heure", ""):
                    with open("archive_tempo.json", "w", encoding="utf-8") as f:
                        json.dump([fields], f, indent=4, ensure_ascii=False)
                    print(f"✅ SUCCÈS : Donnée du {fields['date_heure']} enregistrée.")
                    return
                else:
                    print(f"⚠️ Donnée reçue mais c'est du passé : {fields.get('date_heure')}")
            else:
                print("❌ Réponse vide de RTE.")
        else:
            print(f"❌ Le serveur RTE est indisponible (Erreur {response.status_code})")

    except Exception as e:
        print(f"💥 Le serveur RTE ne répond pas (Timeout). Il est probablement en maintenance.")

if __name__ == "__main__":
    job()
