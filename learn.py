import json
import requests
from datetime import datetime, timedelta

def learn_from_history():
    """Analyse les erreurs passées pour ajuster les seuils"""
    
    # Charger l'historique
    with open("stats_fiabilite.json", "r") as f:
        stats = json.load(f)
    
    # Analyser les erreurs
    errors = {
        'temp_too_high_for_red': [],
        'temp_too_low_for_blue': [],
        'gw_too_low_for_red': [],
        'gw_too_high_for_blue': []
    }
    
    for entry in stats.get('history', []):
        if entry['predicted'] != entry['actual']:
            errors[f"predicted_{entry['predicted']}_was_{entry['actual']}"].append({
                'temp': entry['temp'],
                'gw': entry['gw'],
                'month': entry['month']
            })
    
    # Calculer de nouveaux seuils optimaux
    recommendations = {
        'temp_threshold_red': calculate_optimal_threshold(errors, 'temp', 'red'),
        'gw_threshold_red': calculate_optimal_threshold(errors, 'gw', 'red'),
        'accuracy_by_month': {}
    }
    
    # Sauvegarder les recommandations
    with open("learning_output.json", "w") as f:
        json.dump(recommendations, f, indent=4)
    
    print(f"✅ Analyse terminée. Précision actuelle: {stats['j1']['success']}/{stats['j1']['total']}")
    return recommendations
