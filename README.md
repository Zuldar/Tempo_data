# 🎨 Tempo Data - Prévisions Tempo EDF

Système de prévision des couleurs Tempo (Bleu/Blanc/Rouge) basé sur la consommation électrique et la météo.

## 📁 Structure du projet

```
Tempo_data/
├── backend/              # Scripts Python
│   ├── fetch_data.py    # Récupère les données (RTE, météo, Tempo)
│   ├── predict.py       # Génère les prévisions J+1/J+2/J+3
│   ├── validate.py      # Vérifie la précision des prédictions
│   └── config.json      # Configuration des seuils
├── data/                 # Données JSON
│   ├── current.json     # Données temps réel
│   ├── predictions.json # Prévisions générées
│   ├── stats_fiabilite.json  # Statistiques de précision
│   └── history.json     # Historique des prédictions
├── frontend/             # Interface web
│   └── index.html       # Dashboard visuel
└── .github/workflows/    # Automatisation
    └── update.yml       # GitHub Actions
```

## 🚀 Installation locale

```bash
# Cloner le projet
git clone https://github.com/Zuldar/Tempo_data.git
cd Tempo_data

# Installer les dépendances
pip install requests

# Tester la récupération des données
cd backend
python fetch_data.py

# Générer les prévisions
python predict.py

# Valider les prédictions passées
python validate.py
```

## 📊 Sources de données

- **RTE Eco2mix** : Flux électriques et consommation
- **API Tempo** : Couleurs officielles
- **Open-Meteo** : Prévisions météo nationales
- **API Gouv** : Jours fériés français

## 🤖 Automatisation

GitHub Actions met à jour automatiquement :
- Toutes les **5 minutes** : Récupération + Prévisions
- Chaque jour à **12h** : Validation de la précision

## 📈 Algorithme de prévision

L'algorithme combine :
1. **Température ressentie** (pondérée sur 6 grandes villes)
2. **Consommation électrique** prévue (GW)
3. **Jours fériés** (impact -30% consommation)
4. **Saison** (seuils adaptatifs hiver/été)
5. **Jours restants** dans la saison Tempo

### Seuils configurables

Voir `backend/config.json` pour ajuster :
- Seuils de température (hiver/été)
- Seuils de consommation (GW)
- Pondérations (température vs consommation)

## 📱 Interface web

Accessible sur : [https://zuldar.github.io/Tempo_data/frontend/](https://zuldar.github.io/Tempo_data/frontend/)

L'interface affiche :
- ⚡ Flux électriques en temps réel
- 🎨 Couleurs Tempo officielles (J et J+1)
- 🔮 Prévisions J+2 et J+3 avec probabilités
- 📊 Jours restants dans la saison

## 🎯 Précision actuelle

Les statistiques de précision sont disponibles dans `data/stats_fiabilite.json`

## 🔧 Configuration

Pour ajuster les seuils de prévision :

```json
// backend/config.json
{
  "seuils_hiver": {
    "temp": {"extreme": -2, "high": 0, "medium": 4, "low": 8},
    "gw": {"extreme": 85, "high": 78, "medium": 70, "low": 62}
  },
  "poids": {
    "temp_hiver": 0.70,  // 70% température, 30% consommation
    "impact_ferie": 0.70 // -30% consommation les jours fériés
  }
}
```

## 📝 Licence

MIT

## 🤝 Contribution

Les pull requests sont bienvenues ! Pour des changements majeurs, ouvrez d'abord une issue.

---

Made with ⚡ by Zuldar
