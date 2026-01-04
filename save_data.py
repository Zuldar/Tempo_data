import requests
import json
import time

# URL directe du flux temps réel (France entière)
URL_DIRECT = "https://www.rte-france.com/eco2mix/null"

def job():
    try:
        timestamp = time.strftime('%H:%M:%S')
        print(f"[{timestamp}] Interrogation Flux Direct RTE (Simulated Browser)...")
        
        # On ajoute des headers pour ne pas être bloqué
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://www.rte-france.com/eco-2-mix/la-production-d-electricite-par-filiere'
        }

        response = requests.get(URL_DIRECT, headers=headers, timeout=30)
        
        # On vérifie si la réponse est bien du JSON
        if response.status_code != 200:
            print(f"❌ Erreur Serveur : Code {response.status_code}")
            return

        data = response.json()
        
        if "perimetre" in data and len(data["perimetre"]) > 0:
            all_points = data["perimetre"][0]["donnees"]
            valid_entry = None
            
            # On cherche le dernier point valide
            for p in reversed(all_points):
                if p.get("consommation") is not None:
                    valid_entry = p
                    break
            
            if valid_entry:
                date_brute = valid_entry.get("date", "")
                
                # Sauvegarde au format attendu par ton HTML
                output = [{
                    "date_heure": f"{date_brute} {valid_entry.get('heure')}",
                    "heure": valid_entry.get("heure"),
                    "consommation": valid_entry.get("consommation", 0),
                    "nucleaire": valid_entry.get("nucleaire", 0),
                    "eolien": valid_entry.get("eolien", 0),
                    "solaire": valid_entry.get("solaire", 0),
                    "hydraulique": valid_entry.get("hydraulique", 0),
                    "gaz": valid_entry.get("gaz", 0),
                    "bioenergies": valid_entry.get("bioenergies", 0),
                    "ech_comm_angleterre": valid_entry.get("ech_comm_angleterre", 0),
                    "ech_comm_espagne": valid_entry.get("ech_comm_espagne", 0),
                    "ech_comm_italie": valid_entry.get("ech_comm_italie", 0),
                    "ech_comm_suisse": valid_entry.get("ech_comm_suisse", 0),
                    "ech_comm_allemagne_belgique": valid_entry.get("ech_comm_allemagne_belgique", 0),
                    "ech_comm_belgique": valid_entry.get("ech_comm_belgique", 0)
                }]
                
                with open("archive_tempo.json", "w", encoding="utf-8") as f:
                    json.dump(output, f, indent=4, ensure_ascii=False)
                print(f"✅ SUCCÈS : Donnée du {date_brute} à {valid_entry['heure']} sauvegardée.")
            else:
                print("⚠️ Aucune donnée exploitable trouvée dans le flux.")
        else:
            print("❌ Structure JSON inattendue.")
                
    except Exception as e:
        print(f"💥 Erreur lors de l'extraction : {e}")

if __name__ == "__main__":
    job()
