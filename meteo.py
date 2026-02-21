"""
Bulletin meteo automatique : Lausanne, Chatel (Haute-Savoie), Paris.
Utilise l'API Open-Meteo (gratuite, sans cle API).
Lance le script a tout moment : python meteo.py
Le fichier meteo_bulletin.txt sera genere/ecrase a chaque execution.
"""

import requests
from datetime import datetime, timezone
import math
import os
import subprocess
import sys

# ── Configuration des villes ──────────────────────────────────────────────────

VILLES = [
    {
        "nom": "Lausanne",
        "region": "Suisse, canton de Vaud",
        "lat": 46.5197,
        "lon": 6.6323,
        "altitude_info": "~500m",
        "timezone": "Europe/Zurich",
    },
    {
        "nom": "Chatel",
        "region": "Haute-Savoie, France",
        "lat": 46.2667,
        "lon": 6.8417,
        "altitude_info": "~1200m (village), ~2200m (sommet pistes)",
        "timezone": "Europe/Paris",
    },
    {
        "nom": "Paris",
        "region": "Ile-de-France",
        "lat": 48.8566,
        "lon": 2.3522,
        "altitude_info": "~35m",
        "timezone": "Europe/Paris",
    },
]

FICHIER_SORTIE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meteo_bulletin.txt")

# ── Appel API ─────────────────────────────────────────────────────────────────

def fetch_meteo(ville: dict) -> dict:
    """Recupere les donnees meteo via Open-Meteo."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": ville["lat"],
        "longitude": ville["lon"],
        "current": ",".join([
            "temperature_2m", "relative_humidity_2m", "apparent_temperature",
            "precipitation", "rain", "snowfall", "cloud_cover",
            "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m",
            "surface_pressure", "weather_code",
        ]),
        "daily": ",".join([
            "temperature_2m_max", "temperature_2m_min",
            "apparent_temperature_max", "apparent_temperature_min",
            "precipitation_sum", "precipitation_probability_max",
            "rain_sum", "snowfall_sum",
            "wind_speed_10m_max", "wind_gusts_10m_max",
            "wind_direction_10m_dominant",
            "sunrise", "sunset",
            "uv_index_max",
        ]),
        "timezone": ville["timezone"],
        "forecast_days": 1,
    }
    resp = requests.get(url, params=params, timeout=15)
    resp.raise_for_status()
    return resp.json()


# ── Helpers ───────────────────────────────────────────────────────────────────

WEATHER_DESCRIPTIONS = {
    0: "Ciel degage",
    1: "Principalement degage",
    2: "Partiellement nuageux",
    3: "Couvert",
    45: "Brouillard",
    48: "Brouillard givrant",
    51: "Bruine legere",
    53: "Bruine moderee",
    55: "Bruine dense",
    56: "Bruine verglacante legere",
    57: "Bruine verglacante dense",
    61: "Pluie legere",
    63: "Pluie moderee",
    65: "Pluie forte",
    66: "Pluie verglacante legere",
    67: "Pluie verglacante forte",
    71: "Neige legere",
    73: "Neige moderee",
    75: "Neige forte",
    77: "Grains de neige",
    80: "Averses legeres",
    81: "Averses moderees",
    82: "Averses violentes",
    85: "Averses de neige legeres",
    86: "Averses de neige fortes",
    95: "Orage",
    96: "Orage avec grele legere",
    99: "Orage avec grele forte",
}


def desc_weather_code(code: int) -> str:
    return WEATHER_DESCRIPTIONS.get(code, f"Code inconnu ({code})")


def ascii_weather(code: int) -> list[str]:
    """Retourne un petit dessin ASCII 5 lignes selon le weather code."""
    if code <= 1:  # degage
        return [
            r"    \   /    ",
            r"     .-.     ",
            r"  ― (   ) ―  ",
            r"     `-'     ",
            r"    /   \    ",
        ]
    elif code == 2:  # partiellement nuageux
        return [
            r"   \  /      ",
            r" _ /''.--.   ",
            r"   \_(    ). ",
            r"   /(___(__) ",
            r"             ",
        ]
    elif code == 3:  # couvert
        return [
            r"             ",
            r"     .--.    ",
            r"  .-(    ).  ",
            r" (___.__)__) ",
            r"             ",
        ]
    elif code in (45, 48):  # brouillard
        return [
            r"             ",
            r"  _ - _ - _  ",
            r"   _ - _ -   ",
            r"  _ - _ - _  ",
            r"             ",
        ]
    elif code in (51, 53, 55, 56, 57):  # bruine
        return [
            r"     .--.    ",
            r"  .-(    ).  ",
            r" (___.__)__) ",
            r"   ,  ,  ,   ",
            r"  ,  ,  ,    ",
        ]
    elif code in (61, 63, 65, 66, 67, 80, 81, 82):  # pluie
        return [
            r"     .--.    ",
            r"  .-(    ).  ",
            r" (___.__)__) ",
            r"  / / / / /  ",
            r" / / / / /   ",
        ]
    elif code in (71, 73, 75, 77, 85, 86):  # neige
        return [
            r"     .--.    ",
            r"  .-(    ).  ",
            r" (___.__)__) ",
            r"  * * * * *  ",
            r" * * * * *   ",
        ]
    elif code in (95, 96, 99):  # orage
        return [
            r"     .--.    ",
            r"  .-(    ).  ",
            r" (___.__)__) ",
            r"  /_/ /_/ /  ",
            r"   /_ /_/    ",
        ]
    else:
        return [
            r"             ",
            r"     .--.    ",
            r"  .-(    ).  ",
            r" (___.__)__) ",
            r"             ",
        ]


def barre_temperature(t_min: float, t_max: float) -> str:
    """Genere une barre visuelle de temperature."""
    # Echelle de -20 a 40°C sur 30 caracteres
    bar_len = 30
    scale_min, scale_max = -20, 40
    rng = scale_max - scale_min

    pos_min = max(0, min(bar_len, int((t_min - scale_min) / rng * bar_len)))
    pos_max = max(0, min(bar_len, int((t_max - scale_min) / rng * bar_len)))
    if pos_max <= pos_min:
        pos_max = pos_min + 1

    bar = list("." * bar_len)
    for j in range(pos_min, min(pos_max, bar_len)):
        t_at = scale_min + (j / bar_len) * rng
        if t_at < 0:
            bar[j] = "#"
        elif t_at < 10:
            bar[j] = "="
        elif t_at < 25:
            bar[j] = ":"
        else:
            bar[j] = "!"
    return f"  -20°C |{''.join(bar)}| 40°C"


def barre_precip(prob: float) -> str:
    """Genere une barre visuelle de probabilite de precipitation."""
    bar_len = 20
    filled = int((prob / 100) * bar_len)
    bar = "~" * filled + "." * (bar_len - filled)
    return f"  [{bar}] {prob:.0f}%"


def direction_vent(deg: float) -> str:
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSO", "SO", "OSO", "O", "ONO", "NO", "NNO"]
    idx = round(deg / 22.5) % 16
    return dirs[idx]


def beaufort(kmh: float) -> str:
    if kmh < 1:
        return "Calme (0)"
    elif kmh < 6:
        return "Tres legere brise (1)"
    elif kmh < 12:
        return "Legere brise (2)"
    elif kmh < 20:
        return "Petite brise (3)"
    elif kmh < 29:
        return "Jolie brise (4)"
    elif kmh < 39:
        return "Bonne brise (5)"
    elif kmh < 50:
        return "Vent frais (6)"
    elif kmh < 62:
        return "Grand frais (7)"
    elif kmh < 75:
        return "Coup de vent (8)"
    elif kmh < 89:
        return "Fort coup de vent (9)"
    elif kmh < 103:
        return "Tempete (10)"
    elif kmh < 117:
        return "Violente tempete (11)"
    else:
        return "Ouragan (12)"


def point_de_rosee(temp: float, hum: float) -> float:
    a, b = 17.27, 237.7
    alpha = (a * temp) / (b + temp) + math.log(hum / 100.0)
    return round((b * alpha) / (a - alpha), 1)


def duree_jour(sunrise_str: str, sunset_str: str) -> str:
    fmt = "%Y-%m-%dT%H:%M"
    sr = datetime.strptime(sunrise_str, fmt)
    ss = datetime.strptime(sunset_str, fmt)
    delta = ss - sr
    h, reste = divmod(int(delta.total_seconds()), 3600)
    m = reste // 60
    return f"{h}h{m:02d}"


# ── Recommandations vestimentaires ────────────────────────────────────────────

def recommandation(nom: str, data: dict) -> str:
    cur = data["current"]
    daily = data["daily"]

    t_max = daily["temperature_2m_max"][0]
    t_min = daily["temperature_2m_min"][0]
    precip_prob = daily["precipitation_probability_max"][0] or 0
    pluie = daily["rain_sum"][0] or 0
    neige = daily["snowfall_sum"][0] or 0
    vent_max = daily["wind_speed_10m_max"][0] or 0
    rafales = daily["wind_gusts_10m_max"][0] or 0

    lignes = []

    # -- Couche de base / chaleur --
    if t_min < -10:
        lignes.append("- Sous-vetements thermiques OBLIGATOIRES (haut + bas)")
        lignes.append("- Doudoune epaisse ou manteau grand froid")
        lignes.append("- Bonnet, gants doubles, echarpe/tour de cou")
    elif t_min < 0:
        lignes.append("- Sous-couche thermique recommandee")
        lignes.append("- Manteau chaud / doudoune")
        lignes.append("- Bonnet et gants chauds")
        lignes.append("- Echarpe ou tour de cou")
    elif t_min < 5:
        lignes.append("- Pull ou polaire en couche intermediaire")
        lignes.append("- Veste chaude ou manteau mi-saison epais")
        lignes.append("- Echarpe legere pour le matin")
        lignes.append("- Gants legers optionnels")
    elif t_min < 12:
        lignes.append("- Pull leger ou sweat")
        lignes.append("- Veste legere ou blouson")
    elif t_min < 20:
        lignes.append("- T-shirt ou chemise legere")
        lignes.append("- Gilet ou veste fine pour le soir")
    else:
        lignes.append("- Vetements legers et respirants")
        lignes.append("- Chapeau / casquette contre le soleil")

    # -- Pluie / neige --
    if neige > 0:
        lignes.append("- NEIGE prevue : chaussures impermeables et crantees")
        lignes.append("- Pantalon impermeable ou surpantalon")
        lignes.append("- Veste impermeable avec capuche")
        if neige > 5:
            lignes.append("- Guetres si vous marchez en exterieur")
    elif precip_prob >= 70 or pluie > 3:
        lignes.append("- Parapluie INDISPENSABLE")
        lignes.append("- Veste impermeable avec capuche")
        lignes.append("- Chaussures impermeables (pas de baskets en toile !)")
    elif precip_prob >= 40:
        lignes.append("- Parapluie pliable dans le sac (on ne sait jamais)")
        lignes.append("- Veste deperlante ou coupe-vent")
        lignes.append("- Chaussures fermees de preference")
    else:
        lignes.append("- Pas de pluie significative attendue")

    # -- Vent --
    if rafales > 80:
        lignes.append("- VENT FORT : coupe-vent solide obligatoire")
        lignes.append("- Evitez les parapluies, preferez une capuche")
    elif rafales > 50:
        lignes.append("- Vent soutenu : coupe-vent recommande")
    elif vent_max > 25:
        lignes.append("- Brise notable : une couche coupe-vent est un plus")

    # -- UV --
    uv = daily["uv_index_max"][0] or 0
    if uv >= 6:
        lignes.append(f"- UV eleve ({uv:.0f}) : creme solaire et lunettes de soleil")
    elif uv >= 3:
        lignes.append(f"- UV modere ({uv:.0f}) : lunettes de soleil recommandees")

    # -- Verdict --
    lignes.append("")
    if t_min < 0 and neige > 0:
        lignes.append("  Verdict : Conditions hivernales. Habillez-vous chaudement,")
        lignes.append("  impermeabilisez-vous, et soyez prudent sur les sols glissants.")
    elif t_min < 5 and precip_prob >= 50:
        lignes.append("  Verdict : Frais et humide. Le systeme des 3 couches est")
        lignes.append("  votre meilleur ami : thermique + polaire + impermeable.")
    elif t_min < 5:
        lignes.append("  Verdict : Frais mais sec. Un bon manteau et une echarpe")
        lignes.append("  suffiront pour passer la journee confortablement.")
    elif t_max > 25:
        lignes.append("  Verdict : Journee chaude ! Restez leger, hydratez-vous,")
        lignes.append("  et cherchez l'ombre aux heures les plus chaudes.")
    elif precip_prob >= 50:
        lignes.append("  Verdict : Temps mitige. Gardez un parapluie a portee")
        lignes.append("  et privilegiez des chaussures qui ne craignent pas l'eau.")
    else:
        lignes.append("  Verdict : Conditions agreables. Habillez-vous normalement")
        lignes.append("  avec une petite couche en plus pour le matin/soir.")

    return "\n".join(lignes)


# ── Construction du bulletin ──────────────────────────────────────────────────

def construire_bulletin(resultats: list[tuple[dict, dict]]) -> str:
    maintenant = datetime.now()
    date_str = maintenant.strftime("%A %d %B %Y").capitalize()
    heure_str = maintenant.strftime("%Hh%M")

    JOURS_FR = {
        "Monday": "Lundi", "Tuesday": "Mardi", "Wednesday": "Mercredi",
        "Thursday": "Jeudi", "Friday": "Vendredi", "Saturday": "Samedi",
        "Sunday": "Dimanche",
    }
    MOIS_FR = {
        "January": "janvier", "February": "fevrier", "March": "mars",
        "April": "avril", "May": "mai", "June": "juin", "July": "juillet",
        "August": "aout", "September": "septembre", "October": "octobre",
        "November": "novembre", "December": "decembre",
    }
    for en, fr in JOURS_FR.items():
        date_str = date_str.replace(en, fr)
    for en, fr in MOIS_FR.items():
        date_str = date_str.replace(en, fr)
        date_str = date_str.replace(en.lower(), fr)
        date_str = date_str.replace(en.upper(), fr.upper())

    W = 80
    lines = []

    # ── Header avec ASCII art ──
    lines.append("+" + "=" * (W - 2) + "+")
    lines.append("|" + " " * (W - 2) + "|")
    banner = [
        r"  __  __      _              ____        _ _      _   _        ",
        r" |  \/  | ___| |_ ___  ___  | __ ) _   _| | | ___| |_(_)_ __  ",
        r" | |\/| |/ _ \ __/ _ \/ _ \ |  _ \| | | | | |/ _ \ __| | '_ \ ",
        r" | |  | |  __/ ||  __/ (_) || |_) | |_| | | |  __/ |_| | | | |",
        r" |_|  |_|\___|\__\___|\___/ |____/ \__,_|_|_|\___|\__|_|_| |_|",
    ]
    for b in banner:
        lines.append("|" + b.center(W - 2) + "|")
    lines.append("|" + " " * (W - 2) + "|")
    lines.append("|" + f"  {date_str}".center(W - 2) + "|")
    lines.append("|" + f"  Genere a {heure_str}".center(W - 2) + "|")
    lines.append("|" + "  Lausanne  ~  Chatel (74)  ~  Paris".center(W - 2) + "|")
    lines.append("|" + " " * (W - 2) + "|")
    lines.append("+" + "=" * (W - 2) + "+")
    lines.append("")

    comparatif = []

    for i, (ville, data) in enumerate(resultats, 1):
        cur = data["current"]
        daily = data["daily"]

        t_cur = cur["temperature_2m"]
        t_res = cur["apparent_temperature"]
        hum = cur["relative_humidity_2m"]
        nuages = cur["cloud_cover"]
        vent = cur["wind_speed_10m"]
        vent_dir = cur["wind_direction_10m"]
        rafales = cur["wind_gusts_10m"]
        pression = cur["surface_pressure"]
        wcode = cur["weather_code"]

        t_max = daily["temperature_2m_max"][0]
        t_min = daily["temperature_2m_min"][0]
        tres_max = daily["apparent_temperature_max"][0]
        tres_min = daily["apparent_temperature_min"][0]
        precip_prob = daily["precipitation_probability_max"][0] or 0
        pluie_total = daily["rain_sum"][0]
        neige_total = daily["snowfall_sum"][0]
        vent_max = daily["wind_speed_10m_max"][0]
        raf_max = daily["wind_gusts_10m_max"][0]
        vent_dom = daily["wind_direction_10m_dominant"][0]
        sunrise = daily["sunrise"][0]
        sunset = daily["sunset"][0]
        uv_max = daily["uv_index_max"][0]

        # ── Titre ville ──
        titre = f"  {i}. {ville['nom'].upper()} ({ville['region']}) ~ Alt. {ville['altitude_info']}  "
        pad = W - len(titre)
        lines.append("+" + "-" * (W - 2) + "+")
        lines.append("|" + titre + " " * max(0, pad - 2) + "|")
        lines.append("+" + "-" * (W - 2) + "+")

        # ── ASCII art meteo + resume cote a cote ──
        art = ascii_weather(wcode)
        desc = desc_weather_code(wcode)
        info_lines = [
            f"  {desc}",
            f"  {t_cur}°C  (ressenti {t_res}°C)",
            f"  Min {t_min}°C / Max {t_max}°C",
            f"  Vent {vent} km/h {direction_vent(vent_dir)}  ~  Rafales {rafales} km/h",
            "",
        ]
        lines.append("|" + " " * (W - 2) + "|")
        for j in range(5):
            a = art[j] if j < len(art) else " " * 13
            inf = info_lines[j] if j < len(info_lines) else ""
            line_content = f"    {a}  |{inf}"
            lines.append("|" + line_content + " " * max(0, W - 2 - len(line_content)) + "|")
        lines.append("|" + " " * (W - 2) + "|")

        # ── Barre temperature ──
        lines.append("|  Temperature du jour :".ljust(W - 1) + "|")
        lines.append("|" + barre_temperature(t_min, t_max).ljust(W - 2) + "|")
        lines.append("|" + f"  [ # = negatif | = = 0-10°C | : = 10-25°C | ! = 25°C+ ]".ljust(W - 2) + "|")
        lines.append("|" + " " * (W - 2) + "|")

        # ── Barre precipitation ──
        lines.append("|  Precipitation :".ljust(W - 1) + "|")
        lines.append("|" + barre_precip(precip_prob).ljust(W - 2) + "|")
        if neige_total and neige_total > 0:
            lines.append("|" + f"  *** {neige_total} cm de neige prevus ***".ljust(W - 2) + "|")
        if pluie_total and pluie_total > 0:
            lines.append("|" + f"  ~~~ {pluie_total} mm de pluie prevus ~~~".ljust(W - 2) + "|")
        lines.append("|" + " " * (W - 2) + "|")

        # ── Section nerdy ──
        lines.append("|  .--------------------------------------------.".ljust(W - 1) + "|")
        lines.append("|  |        DONNEES DETAILLEES (nerds only)     |".ljust(W - 1) + "|")
        lines.append("|  '--------------------------------------------'".ljust(W - 1) + "|")
        nerd_data = [
            f"  Couverture nuageuse .. {nuages}%",
            f"  Humidite relative .... {hum}%",
            f"  Point de rosee ....... {point_de_rosee(t_cur, hum)}°C",
            f"  Pression atmo ........ {pression} hPa",
            f"  Vent max journee ..... {vent_max} km/h ({beaufort(vent_max)})",
            f"  Rafales max .......... {raf_max} km/h",
            f"  Direction dominante .. {direction_vent(vent_dom)} ({vent_dom}°)",
            f"  Ressenti min/max ..... {tres_min}°C / {tres_max}°C",
            f"  Indice UV max ........ {uv_max}",
            f"  Lever du soleil ...... {sunrise.split('T')[1]}",
            f"  Coucher du soleil .... {sunset.split('T')[1]}",
            f"  Duree du jour ........ {duree_jour(sunrise, sunset)}",
        ]
        for nd in nerd_data:
            lines.append("|" + nd.ljust(W - 2) + "|")
        lines.append("|" + " " * (W - 2) + "|")
        lines.append("+" + "-" * (W - 2) + "+")
        lines.append("")

        # Donnees pour le comparatif
        type_precip = "Neige" if (neige_total or 0) > 0 else "Pluie" if (pluie_total or 0) > 0 else "Sec"
        comparatif.append({
            "nom": ville["nom"],
            "t_min": t_min,
            "t_max": t_max,
            "precip": f"{type_precip} {precip_prob:.0f}%",
            "vent": f"{vent_max} km/h",
            "confort_score": t_max - precip_prob / 10 - (vent_max or 0) / 10,
            "wcode": wcode,
        })

    # ── Recommandations vestimentaires ──
    lines.append("+" + "=" * (W - 2) + "+")
    lines.append("|" + "  RECOMMANDATIONS VESTIMENTAIRES".center(W - 2) + "|")
    lines.append("+" + "=" * (W - 2) + "+")
    lines.append("")

    for ville, data in resultats:
        wcode = data["current"]["weather_code"]
        art = ascii_weather(wcode)
        lines.append(f"    >>> {ville['nom'].upper()} <<<")
        lines.append("")
        reco = recommandation(ville["nom"], data)
        for rl in reco.split("\n"):
            lines.append(f"    {rl}")
        lines.append("")

    # ── Comparatif ──
    lines.append("+" + "=" * (W - 2) + "+")
    lines.append("|" + "  COMPARATIF RAPIDE".center(W - 2) + "|")
    lines.append("+" + "=" * (W - 2) + "+")
    lines.append("")
    lines.append(f"    {'Ville':<12} {'Temp Min':>9}  {'Temp Max':>9}  {'Precip':<13} {'Vent':<11}")
    lines.append(f"    {'~'*12} {'~'*9}  {'~'*9}  {'~'*13} {'~'*11}")
    for c in comparatif:
        lines.append(f"    {c['nom']:<12} {c['t_min']:>7}°C  {c['t_max']:>7}°C  {c['precip']:<13} {c['vent']:<11}")
    lines.append("")

    # ── Classement confort ──
    medailles = ["[1er]", "[2e] ", "[3e] "]
    classement = sorted(comparatif, key=lambda x: x["confort_score"], reverse=True)
    lines.append("    Classement confort du jour :")
    lines.append("")
    for idx, c in enumerate(classement):
        medal = medailles[idx] if idx < len(medailles) else f"[{idx+1}e] "
        bar_score = ">" * max(1, int(c["confort_score"]))
        lines.append(f"      {medal}  {c['nom']:<12}  {bar_score}")
    lines.append("")

    # ── Footer ──
    lines.append("+" + "-" * (W - 2) + "+")
    lines.append("|" + f"  Source : API Open-Meteo (open-meteo.com)".ljust(W - 2) + "|")
    lines.append("|" + f"  Bulletin genere le {maintenant.strftime('%d/%m/%Y a %Hh%M')}".ljust(W - 2) + "|")
    lines.append("+" + "-" * (W - 2) + "+")
    lines.append("")
    lines.append("      Merci d'avoir consulte le bulletin. Bonne journee !")
    lines.append("")

    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("Recuperation des donnees meteo...")
    resultats = []
    for ville in VILLES:
        print(f"  -> {ville['nom']}...", end=" ")
        try:
            data = fetch_meteo(ville)
            resultats.append((ville, data))
            print("OK")
        except Exception as e:
            print(f"ERREUR : {e}")
            return

    print("Generation du bulletin...")
    bulletin = construire_bulletin(resultats)

    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        f.write(bulletin)

    print(f"Bulletin sauvegarde dans : {FICHIER_SORTIE}")
    print()
    print(bulletin)

    # Ouvre le fichier txt automatiquement
    if sys.platform == "win32":
        os.startfile(FICHIER_SORTIE)
    elif sys.platform == "darwin":
        subprocess.run(["open", FICHIER_SORTIE])
    else:
        subprocess.run(["xdg-open", FICHIER_SORTIE])


if __name__ == "__main__":
    main()
