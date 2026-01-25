import json
from datetime import datetime, timedelta

def load_json(filepath):
    """Charge un fichier JSON"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"❌ Erreur lecture {filepath}: {e}")
        return None

def save_json(filepath, data):
    """Sauvegarde un fichier JSON"""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Erreur écriture {filepath}: {e}")
        return False

def initialize_stats():
    """Initialise le fichier de stats s'il n'existe pas"""
    return {
        "derniere_mise_a_jour": datetime.now().isoformat(),
        "j1": {"success": 0, "total": 0, "taux": 100},
        "j2": {"success": 0, "total": 0, "taux": 100},
        "j3": {"success": 0, "total": 0, "taux": 100},
        "historique": [],
        "erreurs_par_type": {
            "faux_rouge": 0,
            "faux_blanc": 0,
            "faux_bleu": 0
        }
    }

def validate_predictions():
    """
    Compare les prédictions passées avec les couleurs officielles
    Met à jour les statistiques de fiabilité
    """
    print("🔍 Validation des prédictions...")
    
    # Charger les données
    current = load_json("../data/current.json")
    predictions = load_json("../data/predictions.json")
    stats = load_json("../data/stats_fiabilite.json")
    history = load_json("../data/history.json")
    
    # Initialiser si nécessaire
    if not stats:
        stats = initialize_stats()
    
    if not history:
        history = {"predictions": []}
    
    if not current:
        print("⚠️  Données manquantes, validation impossible")
        return
    
    # Récupérer la couleur officielle d'aujourd'hui
    tempo = current.get("tempo_officiel", {})
    today_official = tempo.get("today", {})
    today_code = today_official.get("code")
    today_color = today_official.get("couleur")
    
    if not today_color:
        print("⚠️  Couleur officielle non disponible")
        return
    
    # Date d'aujourd'hui
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📅 Validation pour {today_date} : couleur officielle = {today_color}")
    
    # 🔥 VALIDER J+1, J+2 et J+3
    for days_ago in [1, 2, 3]:
        j_label = f"j{days_ago}"
        
        # Chercher la prédiction faite il y a X jours
        target_past_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        
        # Chercher dans l'historique
        found_prediction = None
        for h in reversed(history.get("predictions", [])):
            h_date = datetime.fromisoformat(h.get("timestamp", "")).strftime("%Y-%m-%d")
            
            if h_date == target_past_date:
                # Chercher la prédiction pour aujourd'hui dans cet historique
                for pred in h.get("predictions", []):
                    if pred.get("date") == today_date:
                        found_prediction = pred
                        break
                break
        
        if found_prediction:
            predicted_color = found_prediction.get("couleur_predite")
            is_correct = (predicted_color == today_color)
            
            # Mettre à jour stats
            stats[j_label]["total"] += 1
            if is_correct:
                stats[j_label]["success"] += 1
                print(f"✅ Prédiction J+{days_ago} correcte : {predicted_color}")
            else:
                print(f"❌ Prédiction J+{days_ago} incorrecte : {predicted_color} ≠ {today_color}")
                
                # Tracker type d'erreur (seulement pour J+1)
                if days_ago == 1:
                    if predicted_color == "ROUGE" and today_color != "ROUGE":
                        stats["erreurs_par_type"]["faux_rouge"] += 1
                    elif predicted_color == "BLANC" and today_color != "BLANC":
                        stats["erreurs_par_type"]["faux_blanc"] += 1
                    elif predicted_color == "BLEU" and today_color != "BLEU":
                        stats["erreurs_par_type"]["faux_bleu"] += 1
            
            # Calculer taux de réussite
            if stats[j_label]["total"] > 0:
                stats[j_label]["taux"] = round((stats[j_label]["success"] / stats[j_label]["total"]) * 100, 1)
            
            # Ajouter à l'historique (seulement J+1 pour ne pas dupliquer)
            if days_ago == 1:
                stats["historique"].append({
                    "date": today_date,
                    "predit": predicted_color,
                    "reel": today_color,
                    "correct": is_correct,
                    "metadata": found_prediction.get("metadata", {})
                })
                
                # Limiter l'historique aux 100 derniers
                if len(stats["historique"]) > 100:
                    stats["historique"] = stats["historique"][-100:]
        else:
            print(f"⏭️  Pas de prédiction J+{days_ago} à valider (prédiction faite le {target_past_date} non trouvée)")
    
    # Mettre à jour timestamp
    stats["derniere_mise_a_jour"] = datetime.now().isoformat()
    
    # Sauvegarder les stats
    save_json("../data/stats_fiabilite.json", stats)
    
    # Archiver les prédictions actuelles dans l'historique
    if predictions:
        if "predictions" not in history:
            history["predictions"] = []
        
        history["predictions"].append({
            "timestamp": predictions.get("timestamp"),
            "predictions": predictions.get("predictions", [])
        })
        
        # Limiter à 30 jours d'historique
        if len(history["predictions"]) > 30:
            history["predictions"] = history["predictions"][-30:]
        
        save_json("../data/history.json", history)
    
    # Afficher résumé
    print(f"\n📊 Statistiques de fiabilité :")
    print(f"  J+1: {stats['j1']['success']}/{stats['j1']['total']} ({stats['j1']['taux']}%)")
    print(f"  J+2: {stats['j2']['success']}/{stats['j2']['total']} ({stats['j2']['taux']}%)")
    print(f"  J+3: {stats['j3']['success']}/{stats['j3']['total']} ({stats['j3']['taux']}%)")
    print(f"\n🎯 Erreurs par type :")
    print(f"  Faux rouges: {stats['erreurs_par_type']['faux_rouge']}")
    print(f"  Faux blancs: {stats['erreurs_par_type']['faux_blanc']}")
    print(f"  Faux bleus: {stats['erreurs_par_type']['faux_bleu']}")
    
    print("\n✅ Validation terminée")

if __name__ == "__main__":
    validate_predictions()
