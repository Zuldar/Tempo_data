import requests
import json
import time

# On utilise l'API v2.1 qui est la plus réactive en 2026
# Le paramètre &cb= permet de forcer la mise à jour (Anti-Cache)
timestamp = int(time.time())
URL = f"https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?order_by=date_heure%20desc&limit=10&cb={timestamp}"

def job():
    try:
        print(f"Interrogation de RTE (Flux 2026) à {time.strftime('%H:%M:%S')}...")
        response = requests.get(URL, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        valid_entry = None
        if "results" in data and len(data["results"]) > 0:
            for entry in data["results"]:
                # Sécurité : On vérifie que la conso est remplie et qu'on est bien en 2026
                conso = entry.get("consommation")
                date_str = entry.get("date_heure", "")
                
                if conso is not None and conso > 0 and "2026" in date_str:
                    valid_entry = entry
                    print(f"✅ Donnée trouvée : {date_str} | Conso: {conso} MW")
                    break
            
            if valid_entry:
                # On définit le nom du fichier que le robot doit enregistrer
                filename = "archive_tempo.json"
                
                # On enregistre une LISTE contenant l'objet unique
                # Le mode 'w' efface l'ancien contenu (ton historique pollué)
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump([valid_entry], f, indent=4, ensure_ascii=False)
                
                print(f"🚀 Fichier {filename} mis à jour sur le serveur.")
            else:
                print("⚠️ Aucune donnée valide de 2026 trouvée dans les derniers résultats.")
        else:
            print("❌ L'API RTE ne renvoie aucun résultat actuellement.")
                
    except Exception as e:
        print(f"💥 Erreur critique : {e}")

if __name__ == "__main__":
    job()
