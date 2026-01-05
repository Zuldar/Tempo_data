import requests
import json
import sys

# API RTE pour les flux (MW)
URL_RTE = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-national-tr/records?where=date%3D%222026-01-05%22&order_by=date_heure%20desc&limit=1"

# API Energy-Charts pour les prix (€/MWh) - On récupère les prix du jour
URL_PRICES = "https://api.energy-charts.info/price?zone=fr"

def job():
    try:
        # 1. Récupération des Flux MW
        res_rte = requests.get(URL_RTE, timeout=15)
        data_rte = res_rte.json()["results"][0]
        heure_flux = data_rte.get("heure")

        # 2. Récupération des Prix (Exemple pour les zones connectées)
        # Note: Pour un robot parfait, il faudrait boucler sur chaque zone (de, ch, it, es, gb)
        # Ici on simule l'appel pour simplifier la structure JSON
        zones = ["fr", "de", "ch", "it", "es", "gb"]
        prix_actuels = {}
        
        for zone in zones:
            try:
                p_res = requests.get(f"https://api.energy-charts.info/price?zone={zone}", timeout=5)
                # On récupère le prix correspondant à l'heure actuelle (index de l'heure)
                h_index = int(heure_flux.split(':')[0])
                prix_actuels[zone] = p_res.json()["price"][h_index]
            except:
                prix_actuels[zone] = 0 # Valeur de secours

        output = [{
            "date": data_rte.get("date"),
            "heure": heure_flux,
            "prix_france": prix_actuels["fr"],
            "pays": {
                "UK": {"mw": data_rte.get("ech_comm_angleterre", 0), "prix": prix_actuels["gb"]},
                "ES": {"mw": data_rte.get("ech_comm_espagne", 0), "prix": prix_actuels["es"]},
                "IT": {"mw": data_rte.get("ech_comm_italie", 0), "prix": prix_actuels["it"]},
                "CH": {"mw": data_rte.get("ech_comm_suisse", 0), "prix": prix_actuels["ch"]},
                "DE_BE": {"mw": data_rte.get("ech_comm_allemagne_belgique", 0), "prix": prix_actuels["de"]}
            }
        }]

        with open("archive_tempo.json", "w", encoding="utf-8") as file:
            json.dump(output, file, indent=4, ensure_ascii=False)
        print(f"✅ Données synchronisées à {heure_flux}")

    except Exception as e:
        print(f"❌ Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    job()
