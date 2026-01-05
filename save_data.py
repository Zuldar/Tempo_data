import requests
import json
import time

# URL API Explore V2.1
TARGET_URL = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=20"
PROXY_URL = "https://api.allorigins.win/get?url="

def job():
    try:
        print(f"[{time.strftime('%H:%M:%S')}] Analyse des flux d'échanges commerciaux...")
        
        encoded_url = requests.utils.quote(TARGET_URL)
        full_url = f"{PROXY_URL}{encoded_url}&cb={int(time.time())}"
        
        response = requests.get(full_url, timeout=30)
        wrapper = response.json()
        data = json.loads(wrapper['contents'])
        
        valid_entry = None
        
        if "results" in data:
            for record in data["results"]:
                # On cherche un point qui a la consommation ET au moins un flux d'échange non nul
                # C'est la garantie que le point est "complet"
                has_conso = record.get("consommation") is not None
                has_flux = record.get("ech_comm_angleterre") is not None or record.get("ech_comm_italie") is not None
                
                if has_conso and has_flux:
                    valid_entry = record
                    print(f"💎 Point complet trouvé : {record.get('date_heure')}")
                    break
            
            if not valid_entry and len(data["results"]) > 0:
                # Si aucun point n'a de flux, on prend le plus récent avec conso quand même
                valid_entry = data["results"][0]
                print("⚠️ Aucun point avec flux trouvé, repli sur le dernier point conso.")

            if valid_entry:
                output = [{
                    "date_heure": valid_entry.get("date_heure"),
                    "heure": valid_entry.get("heure"),
                    "consommation": valid_entry.get("consommation", 0),
                    "nucleaire": valid_entry.get("nucleaire", 0),
                    "eolien": valid_entry.get("eolien", 0),
                    "solaire": valid_entry.get("solaire", 0),
                    "hydraulique": valid_entry.get("hydraulique", 0),
                    "gaz": valid_entry.get("gaz", 0),
                    "bioenergies": valid_entry.get("bioenergies", 0),
                    # Les clés exactes que tu as demandées
                    "ech_comm_angleterre": valid_entry.get("ech_comm_angleterre", 0),
                    "ech_comm_espagne": valid_entry.get("ech_comm_espagne", 0),
                    "ech_comm_italie": valid_entry.get("ech_comm_italie", 0),
                    "ech_comm_suisse": valid_entry.get("ech_comm_suisse", 0),
                    "ech_comm_allemagne_belgique": valid_entry.get("ech_comm_allemagne_belgique", 0),
                    "ech_comm_belgique": valid_entry.get("ech_comm_belgique", 0)
                }]
                
                with open("archive_tempo.json", "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=4, ensure_ascii=False)
                print(f"✅ SUCCÈS : Données (Flux inclus) sauvegardées.")
            else:
                print("❌ Aucune donnée exploitable.")
        
    except Exception as e:
        print(f"💥 Erreur : {e}")

if __name__ == "__main__":
    job()
