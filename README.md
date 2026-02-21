# ⛅ Meteo Dashboard

**Bulletin meteo automatique avec dashboard HTML5 interactif.**

> Donnees en temps reel pour Lausanne, Chatel et Paris — sans cle API.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![API](https://img.shields.io/badge/API-Open--Meteo-00897B)

---

## Fonctionnalites

### Script Python (`meteo.py`)
- **3 villes** — Lausanne (Suisse), Chatel (Haute-Savoie), Paris
- **API Open-Meteo** — gratuite, sans cle, fiable
- **Bulletin complet** — temperature, vent, precipitations, UV, pression, humidite
- **Phase lunaire** — calcul astronomique integre
- **Conseils vestimentaires** — recommandations basees sur la meteo du jour
- **Export texte** — genere un bulletin formate dans `meteo_bulletin.txt`
- **Ouverture auto** — lance le dashboard HTML apres generation

### Dashboard HTML (`index.html`)
- **Fond dynamique** — le gradient de fond change selon la meteo (soleil, pluie, neige, orage...)
- **Variantes jour/nuit** — les couleurs s'adaptent a l'heure
- **Particules animees** — pluie, neige, etoiles, nuages en temps reel sur le canvas
- **Tabs par ville** — navigation fluide entre les 3 villes
- **6 themes** — Sombre, Clair, Ocean, Foret, Rose, Miku
- **Responsive** — s'adapte a toutes les tailles d'ecran

### Donnees affichees
- Temperature actuelle & ressentie, min/max du jour
- Vent (vitesse, rafales, direction avec boussole)
- Precipitations, probabilite de pluie/neige
- Index UV, pression atmospherique, humidite
- Lever/coucher du soleil
- Phase de la lune avec emoji
- Qualite de l'air estimee

## Installation

```bash
# Cloner le repo
git clone https://github.com/SkibidiUlysse/meteo-dashboard.git
cd meteo-dashboard

# Lancer (Python 3.6+)
pip install requests
python meteo.py
```

Le script genere le bulletin et ouvre automatiquement `index.html` dans le navigateur.

## Stack technique

| Composant | Techno |
|-----------|--------|
| Backend | Python 3 + `requests` |
| Frontend | HTML5 Canvas + CSS3 + JS vanilla |
| API | [Open-Meteo](https://open-meteo.com/) (gratuite) |
| Astronomie | Calcul de phase lunaire maison |

---

*La meteo, mais en plus beau.*
