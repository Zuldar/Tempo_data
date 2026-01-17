import requests
import json
from datetime import datetime, timedelta

def fetch_flux_rte():
    """Récupère les flux d'électricité depuis RTE"""
    date_aujourdhui = datetime.now().strftime("%Y-%m-%d")
    url = f"https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?where=date%3D%22{date_aujourdhui}%22&order_by=date_heure%20desc&limit=96"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        results = response.json().get("results", [])
        
        if len(results) > 0:
            f = results[0]
            
            # Trouver la prévision J+1
            prev_val = 0
            for r in results:
                v = r.get("prevision_j1") or r.get("consommation_prevue") or r.get("prev_cons") or 0
                if v > 0:
                    prev_val = v
                    break
            
            return {
                "timestamp": datetime.now().isoformat(),
                "heure": f.get("heure"),
                "date": f.get("date"),
                "consommation_actuelle": f.get("consommation", 0),
                "prevision_j1": prev_val,
                "flux": {
                    "uk": f.get("ech_comm_angleterre", 0),
                    "es": f.get("ech_comm_espagne", 0),
                    "it": f.get("ech_comm_italie", 0),
                    "ch": f.get("ech_comm_suisse", 0),
                    "de_be": f.get("ech_comm_allemagne_belgique", 0)
                }
            }
        return None
    except Exception as e:
        print(f"❌ Erreur fetch_flux_rte: {e}")
        return None

def fetch_meteo():
    """Récupère les prévisions météo pour les 7 prochains jours"""
    # Paris + principales villes pour moyenne pondérée
    cities = [
        {"name": "Paris", "lat": 48.8566, "lon": 2.3522, "weight": 0.3},
        {"name": "Lyon", "lat": 45.7640, "lon": 4.8357, "weight": 0.15},
        {"name": "Marseille", "lat": 43.2965, "lon": 5.3698, "weight": 0.15},
        {"name": "Lille", "lat": 50.6292, "lon": 3.0573, "weight": 0.15},
        {"name": "Toulouse", "lat": 43.6047, "lon": 1.4442, "weight": 0.15},
        {"name": "Strasbourg", "lat": 48.5734, "lon": 7.7521, "weight": 0.1}
    ]
    
    try:
        forecasts = []
        
        for city in cities:
            try:
                url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&daily=temperature_2m_min,temperature_2m_max,windspeed_10m_max&timezone=Europe/Berlin&forecast_days=7"
                response = requests.get(url, timeout=15)
                response.raise_for_status()
                data = response.json()
                
                if "daily" not in data:
                    print(f"⚠️  Pas de données daily pour {city['name']}")
                    continue
                
                forecasts.append({
                    "city": city["name"],
                    "weight": city["weight"],
                    "data": data["daily"]
                })
            except Exception as e:
                print(f"⚠️  Erreur pour {city['name']}: {e}")
                continue
        
        if len(forecasts) == 0:
            print("❌ Aucune donnée météo récupérée")
            return None
        
        # Calculer moyennes pondérées nationales
        national_forecast = []
        for day in range(7):
            try:
                temp_min = sum(f["data"]["temperature_2m_min"][day] * f["weight"] for f in forecasts)
                temp_max = sum(f["data"]["temperature_2m_max"][day] * f["weight"] for f in forecasts)
                wind = sum(f["data"]["windspeed_10m_max"][day] * f["weight"] for f in forecasts)
                
                # Température ressentie approximative
                wind_chill = temp_min - (wind / 5)
                
                date = (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
                
                national_forecast.append({
                    "date": date,
                    "temp_min": round(temp_min, 1),
                    "temp_max": round(temp_max, 1),
                    "temp_ressentie": round(wind_chill, 1),
                    "wind": round(wind, 1)
                })
            except Exception as e:
                print(f"⚠️  Erreur calcul jour {day}: {e}")
                continue
        
        if len(national_forecast) == 0:
            print("❌ Erreur calcul prévisions nationales")
            return None
        
        return national_forecast
        
    except Exception as e:
        print(f"❌ Erreur fetch_meteo: {e}")
        return None

def fetch_tempo_officiel():
    """Récupère les couleurs Tempo officielles"""
    try:
        today = requests.get("https://www.api-couleur-tempo.fr/api/jourTempo/today", timeout=10)
        tomorrow = requests.get("https://www.api-couleur-tempo.fr/api/jourTempo/tomorrow", timeout=10)
        stats = requests.get("https://www.api-couleur-tempo.fr/api/stats", timeout=10)
        
        today.raise_for_status()
        tomorrow.raise_for_status()
        stats.raise_for_status()
        
        t_data = today.json()
        tom_data = tomorrow.json()
        s_data = stats.json()
        
        # Extraction des valeurs
        def find_value(obj, keyword):
            for k, v in obj.items():
                if keyword in k.lower():
                    return v
            return 0
        
        return {
            "today": {
                "code": t_data.get("codeJour"),
                "couleur": {1: "BLEU", 2: "BLANC", 3: "ROUGE"}.get(t_data.get("codeJour"), "INCONNU")
            },
            "tomorrow": {
                "code": tom_data.get("codeJour"),
                "couleur": {1: "BLEU", 2: "BLANC", 3: "ROUGE"}.get(tom_data.get("codeJour"), "INCONNU")
            },
            "saison": {
                "bleu_utilises": find_value(s_data, "bleu"),
                "blanc_utilises": find_value(s_data, "blanc"),
                "rouge_utilises": find_value(s_data, "rouge"),
                "bleu_restants": 300 - find_value(s_data, "bleu"),
                "blanc_restants": 43 - find_value(s_data, "blanc"),
                "rouge_restants": 22 - find_value(s_data, "rouge")
            }
        }
        
    except Exception as e:
        print(f"❌ Erreur fetch_tempo_officiel: {e}")
        return None

def fetch_jours_feries():
    """Récupère les jours fériés de l'année en cours et suivante"""
    year = datetime.now().year
    feries = {}
    
    try:
        for y in [year, year + 1]:
            url = f"https://calendrier.api.gouv.fr/jours-feries/metropole/{y}.json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            feries.update(response.json())
        
        return feries
        
    except Exception as e:
        print(f"❌ Erreur fetch_jours_feries: {e}")
        return {}

def main():
    """Récupère toutes les données et les sauvegarde"""
    print("🔄 Récupération des données...")
    
    # Récupérer toutes les données
    flux = fetch_flux_rte()
    meteo = fetch_meteo()
    tempo = fetch_tempo_officiel()
    feries = fetch_jours_feries()
    
    # Assembler dans un seul fichier
    current_data = {
        "timestamp": datetime.now().isoformat(),
        "flux": flux,
        "meteo": meteo,
        "tempo_officiel": tempo,
        "jours_feries": feries
    }
    
    # Sauvegarder
    with open("../data/current.json", "w", encoding="utf-8") as f:
        json.dump(current_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Données sauvegardées dans data/current.json")
    
    # Affichage résumé
    if flux:
        print(f"  ⚡ Consommation prévue J+1: {flux['prevision_j1']/1000:.1f} GW")
    if meteo:
        print(f"  🌡️  Température demain: {meteo[1]['temp_ressentie']}°C")
    if tempo:
        print(f"  🎨 Aujourd'hui: {tempo['today']['couleur']}")
        print(f"  🎨 Demain: {tempo['tomorrow']['couleur']}")
    
    return current_data

if __name__ == "__main__":
    main()
