import json
from datetime import datetime, timedelta, timezone

# Fuseau horaire français
PARIS_TZ = timezone(timedelta(hours=1))  # UTC+1 en hiver, à ajuster manuellement pour UTC+2 en été

def get_paris_now():
    """Retourne la date/heure actuelle à Paris"""
    return datetime.now(PARIS_TZ)

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
                "temp": {"extreme": 2, "high": 4, "medium": 6, "low": 10},
                "gw": {"extreme": 80, "high": 72, "medium": 65, "low": 58}
            },
            "seuils_ete": {
                "temp": {"extreme": 8, "high": 12, "medium": 16, "low": 20},
                "gw": {"extreme": 75, "high": 68, "medium": 60, "low": 52}
            },
            "poids": {
                "temp_hiver": 0.30,
                "gw_hiver": 0.25,
                "temp_ete": 0.50,
                "gw_ete": 0.30,
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

def calculate_trend_score(temp_today, temp_target, is_winter, config):
    """Calcule le score basé sur la tendance de température"""
    if not is_winter:
        return 0
    
    if "temp_drop" not in config.get("seuils_hiver", {}):
        return 0
    
    temp_drop = temp_today - temp_target
    seuils = config["seuils_hiver"]["temp_drop"]
    
    if temp_drop >= seuils["extreme"]:
        return 100
    elif temp_drop >= seuils["high"]:
        return 70
    elif temp_drop >= seuils["medium"]:
        return 40
    else:
        return 0

def calculate_flux_score(flux_data, is_winter, config):
    """Calcule le score basé sur les imports d'électricité"""
    if not flux_data:
        return 0
    
    if "flux_import" not in config.get("seuils_hiver", {}):
        return 0
    
    solde = sum([
        flux_data.get('uk', 0),
        flux_data.get('es', 0),
        flux_data.get('it', 0),
        flux_data.get('ch', 0),
        flux_data.get('de_be', 0)
    ])
    
    if solde <= 0:
        return 0
    
    seuils = config["seuils_hiver"]["flux_import"]
    
    if solde >= seuils["extreme"]:
        return 100
    elif solde >= seuils["high"]:
        return 70
    elif solde >= seuils["medium"]:
        return 40
    else:
        return 20

def get_recent_colors_stats():
    """Récupère les statistiques des 7 derniers jours"""
    try:
        with open("../data/history.json", "r", encoding="utf-8") as f:
            history = json.load(f)
        
        predictions_history = history.get("predictions", [])
        if not predictions_history:
            return {"recent_reds": 0, "recent_whites": 0}
        
        recent = predictions_history[-7:] if len(predictions_history) >= 7 else predictions_history
        
        reds = 0
        whites = 0
        
        for entry in recent:
            for pred in entry.get("predictions", []):
                color = pred.get("couleur_predite", "")
                if color == "ROUGE":
                    reds += 1
                elif color == "BLANC":
                    whites += 1
        
        return {"recent_reds": reds, "recent_whites": whites}
    except:
        return {"recent_reds": 0, "recent_whites": 0}

def get_day_modifier(day_of_week, config):
    """Retourne le modificateur selon le jour de la semaine"""
    if "modificateurs_jour" not in config:
        return 1.0
    
    days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
    day_name = days[day_of_week]
    return config["modificateurs_jour"].get(day_name, 1.0)

def predict_color(temp, gw, target_date, jours_feries, saison_stats, config, flux_data=None, temp_today=None, history_stats=None):
    """Prédit la couleur Tempo pour une date donnée"""
    date_obj = datetime.strptime(target_date, "%Y-%m-%d")
    day_of_week = date_obj.weekday()
    month = date_obj.month
    
    is_winter = month >= 11 or month <= 2
    is_ferie = is_jour_ferie(target_date, jours_feries)
    
    adjusted_gw = gw * config["poids"]["impact_ferie"] if is_ferie else gw
    
    # Calcul des scores de base
    temp_score = calculate_temp_score(temp, is_winter, config)
    gw_score = calculate_gw_score(adjusted_gw, is_winter, config)
    
    # Nouveaux scores
    trend_score = calculate_trend_score(temp_today if temp_today else temp, temp, is_winter, config) if temp_today else 0
    flux_score = calculate_flux_score(flux_data, is_winter, config) if flux_data else 0
    
    # Pondération
    weights = config["poids"]
    temp_weight = weights.get("temp_hiver", 0.30) if is_winter else weights.get("temp_ete", 0.50)
    gw_weight = weights.get("gw_hiver", 0.25) if is_winter else weights.get("gw_ete", 0.30)
    trend_weight = weights.get("trend_hiver", 0.20) if is_winter else weights.get("trend_ete", 0.10)
    flux_weight = weights.get("flux_hiver", 0.15) if is_winter else weights.get("flux_ete", 0.10)
    
    # Normaliser les poids pour qu'ils totalisent 1.0
    total_weight = temp_weight + gw_weight + trend_weight + flux_weight
    if total_weight > 0:
        temp_weight /= total_weight
        gw_weight /= total_weight
        trend_weight /= total_weight
        flux_weight /= total_weight
    
    global_score = (
        (temp_score * temp_weight) +
        (gw_score * gw_weight) +
        (trend_score * trend_weight) +
        (flux_score * flux_weight)
    )
    
    # Modificateur jour de la semaine
    day_modifier = get_day_modifier(day_of_week, config)
    global_score *= day_modifier
    
    # Pénalité quota
    if history_stats and "quota_management" in config:
        quota_config = config["quota_management"]
        
        if history_stats.get("recent_reds", 0) >= quota_config.get("recent_reds_threshold", 3):
            global_score *= quota_config.get("recent_reds_penalty", 0.75)
        
        if history_stats.get("recent_whites", 0) >= quota_config.get("recent_whites_threshold", 8):
            global_score *= quota_config.get("recent_whites_penalty", 0.85)
    
    if is_ferie:
        global_score *= config["poids"]["reduction_ferie"]
    
    # Ajustement jours restants
    rouge_restants = saison_stats.get("rouge_restants", 22)
    blanc_restants = saison_stats.get("blanc_restants", 43)
    
    rouge_ratio = rouge_restants / 22
    if month >= 2 and rouge_ratio < 0.3:
        global_score *= 1.15
    
    # Distribution probabilités
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
    is_weekend = day_of_week in [5, 6]
    
    if is_weekend or is_ferie:
        w += r
        r = 0
    
    if day_of_week == 6:
        b = 100
        w = 0
        r = 0
    
    if month > 3 and month < 11:
        r = 0
    
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
            "gw_score": gw_score,
            "trend_score": trend_score,
            "flux_score": flux_score,
            "day_modifier": day_modifier
        }
    }

def main():
    """Génère les prévisions J+1, J+2, J+3"""
    print("🔮 Génération des prévisions...")
    
    data = load_data()
    config = load_config()
    
    if not data:
        print("❌ Pas de données disponibles")
        return
    
    meteo = data.get("meteo")
    flux = data.get("flux")
    tempo = data.get("tempo_officiel")
    feries = data.get("jours_feries", {})
    
    history_stats = get_recent_colors_stats()
    print(f"📊 Stats récentes: {history_stats['recent_reds']} rouges, {history_stats['recent_whites']} blancs (7 derniers jours)")
    
    flux_data = flux.get("flux") if flux else None
    
    if not meteo or not isinstance(meteo, list) or len(meteo) == 0:
        print("❌ Données météo manquantes ou invalides")
        return
    
    if not flux:
        print("⚠️  Données de flux manquantes, utilisation valeur par défaut")
        gw_prevision = 65.0
    else:
        gw_prevision = flux.get("prevision_j1", 65000) / 1000
    
    if not tempo:
        print("⚠️  Données Tempo manquantes, utilisation valeurs par défaut")
        saison_stats = {"rouge_restants": 22, "blanc_restants": 43}
    else:
        saison_stats = tempo.get("saison", {"rouge_restants": 22, "blanc_restants": 43})
    
    predictions = []
    
    # 🔥 Utiliser l'heure de Paris au lieu de UTC
    today = get_paris_now()
    target_dates = {
        1: (today + timedelta(days=1)).strftime("%Y-%m-%d"),
        2: (today + timedelta(days=2)).strftime("%Y-%m-%d"),
        3: (today + timedelta(days=3)).strftime("%Y-%m-%d")
    }
    
    print(f"📅 Date actuelle (Paris): {today.strftime('%Y-%m-%d %H:%M')}")
    print(f"📅 Cibles: J+1={target_dates[1]}, J+2={target_dates[2]}, J+3={target_dates[3]}")
    
    temp_today = None
    for m in meteo:
        if m.get("date") == today.strftime("%Y-%m-%d"):
            temp_today = m.get("temp_ressentie")
            break
    
    for offset in [1, 2, 3]:
        target_date = target_dates[offset]
        
        forecast = None
        for m in meteo:
            if m.get("date") == target_date:
                forecast = m
                break
        
        if not forecast:
            print(f"⚠️  Pas de données météo pour J+{offset} ({target_date})")
            continue
        
        if "temp_ressentie" not in forecast:
            print(f"⚠️  Données météo J+{offset} invalides, ignoré")
            continue
        
        try:
            prediction = predict_color(
                temp=forecast["temp_ressentie"],
                gw=gw_prevision,
                target_date=target_date,
                jours_feries=feries,
                saison_stats=saison_stats,
                config=config,
                flux_data=flux_data,
                temp_today=temp_today,
                history_stats=history_stats
            )
            predictions.append(prediction)
            
            print(f"  J+{offset} ({target_date}): {prediction['couleur_predite']} "
                  f"({prediction['probabilites'][prediction['couleur_predite']]}% - "
                  f"Confiance: {prediction['confiance']}) "
                  f"[Score: {prediction['metadata']['global_score']}]")
        except Exception as e:
            print(f"❌ Erreur prédiction J+{offset}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    if len(predictions) == 0:
        print("❌ Aucune prédiction générée")
        return
    
    output = {
        "timestamp": get_paris_now().isoformat(),
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
