import json
from datetime import datetime, timedelta

def load_data():
    """Charge les données actuelles"""
    try:
        with open("../data/current.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Erreur chargement données: {e}")
        return None

def load_config():
    """Charge la configuration des seuils"""
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        # Configuration par défaut
        return {
            "seuils_hiver": {
                "temp": {"extreme": -2, "high": 0, "medium": 4, "low": 8},
                "gw": {"extreme": 85, "high": 78, "medium": 70, "low": 62}
            },
            "seuils_ete": {
                "temp": {"extreme": 8, "high": 12, "medium": 16, "low": 20},
                "gw": {"extreme": 75, "high": 68, "medium": 60, "low": 52}
            },
            "poids": {
                "temp_hiver": 0.70,
                "temp_ete": 0.50,
                "impact_ferie": 0.70,
                "reduction_ferie": 0.85
            }
        }

def is_jour_ferie(date_str, jours_feries):
    """Vérifie si une date est un jour férié"""
    if not jours_feries:
        return False
    return date_str in jours_feries

def calculate_temp_score(temp, is_winter, config):
    """Calcule le score basé sur la température"""
    seuils = config["seuils_hiver"]["temp"] if is_winter else config["seuils_ete"]["temp"]
    
    if temp <= seuils["extreme"]:
        return 100
    elif temp <= seuils["high"]:
        return 85
    elif temp <= seuils["medium"]:
        return 55
    elif temp <= seuils["low"]:
        return 25
    else:
        return 0

def calculate_gw_score(gw, is_winter, config):
    """Calcule le score basé sur la consommation (GW)"""
    seuils = config["seuils_hiver"]["gw"] if is_winter else config["seuils_ete"]["gw"]
    
    if gw >= seuils["extreme"]:
        return 100
    elif gw >= seuils["high"]:
        return 80
    elif gw >= seuils["medium"]:
        return 50
    elif gw >= seuils["low"]:
        return 20
    else:
        return 0

def predict_color(temp, gw, target_date, jours_feries, saison_stats, config):
    """
    Prédit la couleur Tempo pour une date donnée
    
    Args:
        temp: Température ressentie
        gw: Consommation en GW
        target_date: Date cible (string YYYY-MM-DD)
        jours_feries: Dict des jours fériés
        saison_stats: Stats de la saison (jours restants)
        config: Configuration des seuils
    
    Returns:
        dict avec probabilités et métadonnées
    """
    date_obj = datetime.strptime(target_date, "%Y-%m-%d")
    day_of_week = date_obj.weekday()  # 0=lundi, 6=dimanche
    month = date_obj.month
    
    # Déterminer si période critique (hiver)
    is_winter = month >= 11 or month <= 2
    
    # Vérifier jour férié
    is_ferie = is_jour_ferie(target_date, jours_feries)
    
    # Ajuster la consommation si jour férié
    adjusted_gw = gw * config["poids"]["impact_ferie"] if is_ferie else gw
    
    # Calcul des scores
    temp_score = calculate_temp_score(temp, is_winter, config)
    gw_score = calculate_gw_score(adjusted_gw, is_winter, config)
    
    # Pondération selon saison
    temp_weight = config["poids"]["temp_hiver"] if is_winter else config["poids"]["temp_ete"]
    gw_weight = 1 - temp_weight
    
    # Score global
    global_score = (temp_score * temp_weight) + (gw_score * gw_weight)
    
    # Réduction si jour férié
    if is_ferie:
        global_score *= config["poids"]["reduction_ferie"]
    
    # Ajustement selon jours restants
    rouge_restants = saison_stats.get("rouge_restants", 22)
    blanc_restants = saison_stats.get("blanc_restants", 43)
    
    rouge_ratio = rouge_restants / 22
    if month >= 2 and rouge_ratio < 0.3:
        global_score *= 1.15  # Augmenter probabilité rouge en fin de saison
    
    # Distribution initiale des probabilités
    if global_score >= 80:
        r, w, b = 85, 15, 0
    elif global_score >= 65:
        r, w, b = 60, 35, 5
    elif global_score >= 50:
        r, w, b = 25, 60, 15
    elif global_score >= 35:
        r, w, b = 10, 50, 40
    elif global_score >= 20:
        r, w, b = 0, 30, 70
    else:
        r, w, b = 0, 10, 90
    
    # Règles strictes
    is_weekend = day_of_week in [5, 6]  # Samedi ou dimanche
    
    if is_weekend or is_ferie:
        w += r
        r = 0
    
    if day_of_week == 6:  # Dimanche
        b = 100
        w = 0
        r = 0
    
    # Hors hiver, pas de rouge
    if month > 3 and month < 11:
        r = 0
    
    # Gestion quota
    if rouge_restants <= 0:
        w += r
        r = 0
    
    if blanc_restants <= 0:
        b += w
        w = 0
    
    # Normalisation
    total = max(1, r + w + b)
    final_r = round((r / total) * 100)
    final_w = round((w / total) * 100)
    final_b = 100 - (final_r + final_w)
    
    # Couleur dominante
    probs = {"ROUGE": final_r, "BLANC": final_w, "BLEU": max(0, final_b)}
    dominant = max(probs.keys(), key=lambda k: probs[k])
    
    return {
        "date": target_date,
        "couleur_predite": dominant,
        "probabilites": probs,
        "confiance": "HIGH" if probs[dominant] >= 70 else "MEDIUM" if probs[dominant] >= 50 else "LOW",
        "metadata": {
            "temp": temp,
            "gw": gw,
            "adjusted_gw": round(adjusted_gw, 1),
            "is_ferie": is_ferie,
            "is_weekend": is_weekend,
            "global_score": round(global_score, 1),
            "temp_score": temp_score,
            "gw_score": gw_score
        }
    }

def main():
    """Génère les prévisions J+1, J+2, J+3"""
    print("🔮 Génération des prévisions...")
    
    # Charger données et config
    data = load_data()
    config = load_config()
    
    if not data:
        print("❌ Pas de données disponibles")
        return
    
    # Extraire les infos nécessaires
    meteo = data.get("meteo")
    flux = data.get("flux")
    tempo = data.get("tempo_officiel")
    feries = data.get("jours_feries", {})
    
    # 🔥 VÉRIFICATIONS AJOUTÉES
    if not meteo or not isinstance(meteo, list) or len(meteo) == 0:
        print("❌ Données météo manquantes ou invalides")
        return
    
    if not flux:
        print("⚠️  Données de flux manquantes, utilisation valeur par défaut")
        gw_prevision = 65.0
    else:
        gw_prevision = flux.get("prevision_j1", 65000) / 1000  # Convertir en GW
    
    if not tempo:
        print("⚠️  Données Tempo manquantes, utilisation valeurs par défaut")
        saison_stats = {"rouge_restants": 22, "blanc_restants": 43}
    else:
        saison_stats = tempo.get("saison", {"rouge_restants": 22, "blanc_restants": 43})
    
    # Générer prévisions pour J+1, J+2, J+3
    predictions = []
    
    for offset in [1, 2, 3]:
        if offset < len(meteo):
            forecast = meteo[offset]
            
            # Vérifier que les données météo sont valides
            if not forecast or "temp_ressentie" not in forecast or "date" not in forecast:
                print(f"⚠️  Données météo J+{offset} invalides, ignoré")
                continue
            
            try:
                prediction = predict_color(
                    temp=forecast["temp_ressentie"],
                    gw=gw_prevision,
                    target_date=forecast["date"],
                    jours_feries=feries,
                    saison_stats=saison_stats,
                    config=config
                )
                predictions.append(prediction)
                
                print(f"  J+{offset} ({forecast['date']}): {prediction['couleur_predite']} "
                      f"({prediction['probabilites'][prediction['couleur_predite']]}% - "
                      f"Confiance: {prediction['confiance']})")
            except Exception as e:
                print(f"❌ Erreur prédiction J+{offset}: {e}")
                continue
        else:
            print(f"⚠️  Pas de données météo pour J+{offset}")
    
    if len(predictions) == 0:
        print("❌ Aucune prédiction générée")
        return
    
    # Sauvegarder
    output = {
        "timestamp": datetime.now().isoformat(),
        "predictions": predictions
    }
    
    try:
        with open("../data/predictions.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✅ {len(predictions)} prévisions sauvegardées dans data/predictions.json")
    except Exception as e:
        print(f"❌ Erreur sauvegarde: {e}")

if __name__ == "__main__":
    main()
