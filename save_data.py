import requests
import json
import time

# Flux direct Eco2mix (Production Temps Réel)
URL_DIRECT = "https://www.rte-france.com/eco2mix/null"

def job():
    try:
        print(f"[{time.strftime('%H:%M:%S')}] Interrogation Flux Direct RTE...")
        
        # Ce flux renvoie les données de la journée en cours
        response = requests.get(URL_DIRECT, timeout=20)
        data = response.json()
        
        # On récupère le dernier point de mesure (généralement le dernier de la liste)
        if "perimetre" in data and len(data["perimetre"]) > 0:
            # Les données sont dans data['perimetre'][0]['donnees']
            all_points = data["perimetre"][0]["donnees"]
            # On cherche le dernier point qui a une valeur de consommation
            valid_entry = None
            for p in reversed(all_points):
                if p.get("consommation") and p.get("consommation") > 0:
                    valid_entry = p
                    break
            
            if valid_entry:
                # Formatage de la date pour 2026
                # Le flux direct donne souvent 'date': '05/01/2026'
                date_brute = valid_entry.get("date", "")
                
                # SÉCURITÉ : On vérifie qu'on est bien en 2026
                if "2026" in date_brute:
                    # On remappe les clés pour ton HTML
                    output = [{
                        "date_heure": f"{date_brute} {valid_entry.get('heure')}",
                        "heure": valid_entry.get("heure"),
                        "consommation": valid_entry.get("consommation"),
                        "nucleaire": valid_entry.get("nucleaire"),
                        "eolien": valid_entry.get("eolien"),
                        "solaire": valid_entry.get("solaire"),
                        "hydraulique": valid_entry.get("hydraulique"),
                        "gaz": valid_entry.get("gaz"),
                        "bioenergies": valid_entry.get("bioenergies"),
                        "ech_comm_angleterre": valid_entry.get("ech_comm_angleterre"),
                        "ech_comm_espagne": valid_entry.get("ech_comm_espagne"),
                        "ech_comm_italie": valid_entry.get("ech_comm_italie"),
                        "ech_comm_suisse": valid_entry.get("ech_comm_suisse"),
                        "ech_comm_allemagne_belgique": valid_entry.get("ech_comm_allemagne_belgique"),
                        "ech_comm_belgique": valid_entry.get("ech_comm_belgique")
                    }]
                    
                    with open("archive_tempo.json", "w", encoding="utf-8") as f:
                        json.dump(output, f, indent=4, ensure_ascii=False)
                    print(f"✅ SUCCÈS DIRECT : Donnée du {date_brute} à {valid_entry['heure']} sauvegardée.")
                else:
                    print(f"⚠️ Flux direct encore en {date_brute}. RTE n'a pas basculé le direct.")
            else:
                print("❌ Aucune donnée de consommation trouvée dans le flux.")
        else:
            print("❌ Structure de réponse Eco2mix inconnue.")
                
    except Exception as e:
        print(f"💥 Erreur Flux Direct : {e}")

if __name__ == "__main__":
    job()
