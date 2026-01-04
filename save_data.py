import requests
import json
import time

# Nouvelle URL de l'API Explore V2 (plus robuste que l'ancien flux direct)
TARGET_URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=1"
# Proxy pour masquer l'IP de GitHub
PROXY_URL = "https://api.allorigins.win/get?url="

def job():
    try:
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] Connexion via AllOrigins vers API Explore V2...")
        
        # On encode l'URL pour le proxy
        encoded_url = requests.utils.quote(TARGET_URL)
        full_url = f"{PROXY_URL}{encoded_url}&cb={int(time.time())}"
        
        response = requests.get(full_url, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Erreur Proxy/Serveur : {response.status_code}")
            return

        # Extraction du contenu JSON via le wrapper AllOrigins
        wrapper = response.json()
        data = json.loads(wrapper['contents'])
        
        if "results" in data and len(data["results"]) > 0:
            f = data["results"][0]
            
            # On vérifie si on a bien du 2026
            if "2026" not in f.get("date_heure", ""):
                print(f"⚠️ Donnée reçue ({f.get('date_heure')}) mais ce n'est pas encore du 2026.")
                return

            # Sauvegarde au format attendu par ton HTML
            output = [{
                "date_heure": f.get("date_heure"),
                "heure": f.get("heure"),
                "consommation": f.get("consommation", 0),
                "nucleaire": f.get("nucleaire", 0),
                "eolien": f.get("eolien", 0),
                "solaire": f.get("solaire", 0),
                "hydraulique": f.get("hydraulique", 0),
                "gaz": f.get("gaz", 0),
                "bioenergies": f.get("bioenergies", 0),
                "ech_comm_angleterre": f.get("ech_comm_angleterre", 0),
                "ech_comm_espagne": f.get("ech_comm_espagne", 0),
                "ech_comm_italie": f.get("ech_comm_italie", 0),
                "ech_comm_suisse": f.get("ech_comm_suisse", 0),
                "ech_comm_allemagne_belgique": f.get("ech_comm_allemagne_belgique", 0),
                "ech_comm_belgique": f.get("ech_comm_belgique", 0)
            }]
            
            with open("archive_tempo.json", "w", encoding="utf-8") as f:
                json.dump(output, f, indent=4, ensure_ascii=False)
            print(f"✅ SUCCÈS : Donnée du {output[0]['date_heure']} sauvegardée.")
        else:
            print("❌ Aucune donnée trouvée dans les résultats de l'API.")
                
    except Exception as e:
        print(f"💥 Erreur critique : {e}")

if __name__ == "__main__":
    job()
