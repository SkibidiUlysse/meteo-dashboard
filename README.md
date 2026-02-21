<p align="center">
  <h1 align="center">⛅ Meteo Dashboard</h1>
  <p align="center"><strong>Real-time weather intelligence with a cinematic HTML5 dashboard.</strong></p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/Canvas_API-FF6F00?style=for-the-badge&logo=html5&logoColor=white" />
  <img src="https://img.shields.io/badge/Open--Meteo_API-00897B?style=for-the-badge" />
  <img src="https://img.shields.io/badge/No_API_Key-Required-00C853?style=for-the-badge" />
</p>

<p align="center"><em>Weather data for Lausanne, Châtel & Paris — beautifully visualized, no API key needed.</em></p>

---

## How It Works

```
+----------------------------------------------------------------+
|                                                                |
|   meteo.py                          index.html                 |
|   --------                          ----------                 |
|                                                                |
|   +------------+    HTTP GET    +--------------+               |
|   |  3 Cities  |-------------->|  Open-Meteo  |               |
|   |  Configs   |<--------------|  Free API    |               |
|   +-----+------+    JSON resp  +--------------+               |
|         |                                                      |
|         v                                                      |
|   +-----------+    +-----------+    +----------------------+   |
|   |  Weather  |--->|  Lunar    |--->|  Bulletin Generator  |   |
|   |  Decoder  |    |  Phase    |    |  (text + HTML data)  |   |
|   +-----------+    |  Calc     |    +----------+-----------+   |
|                    +-----------+               |               |
|                                                v               |
|                                    +----------------------+    |
|                                    |  Browser auto-open   |    |
|                                    |  index.html          |    |
|                                    +----------+-----------+    |
|                                               |                |
|                                               v                |
|                              +-----------------------------+   |
|                              |  Animated Canvas Dashboard  |   |
|                              |  Rain / Snow / Stars        |   |
|                              |  Dynamic bg / City tabs     |   |
|                              |  Moon phase / Clothing tips |   |
|                              +-----------------------------+   |
|                                                                |
+----------------------------------------------------------------+
```

## Features

### Python Backend (`meteo.py`)
| Feature | Detail |
|---------|--------|
| **3 cities** | Lausanne (CH), Châtel (FR), Paris (FR) |
| **Open-Meteo API** | Free, no key, no rate limit headaches |
| **Full bulletin** | Temp, wind, precipitation, UV, pressure, humidity, sunrise/sunset |
| **Lunar phase** | Astronomical computation — phase name + emoji |
| **Clothing advisor** | What to wear based on today's conditions |
| **Auto-launch** | Generates bulletin → opens dashboard in browser |

### HTML5 Dashboard (`index.html`)
| Feature | Detail |
|---------|--------|
| **Dynamic backgrounds** | Gradient shifts based on weather (sun, rain, snow, storm...) |
| **Day/night variants** | Colors adapt to current hour |
| **Particle engine** | Animated rain drops, snowflakes, stars, clouds on canvas |
| **City tabs** | Smooth navigation between all 3 cities |
| **6 themes** | Dark, Light, Ocean, Forest, Rose, Miku |
| **Responsive** | Looks good on any screen size |

### Data Points
```
Temperature (current, feels-like, min/max)
Wind (speed, gusts, direction with compass)
Precipitation (rain, snow, probability)
UV Index · Atmospheric pressure · Humidity
Sunrise & Sunset times
Moon phase with visual emoji
Estimated air quality
```

## Quick Start

```bash
git clone https://github.com/SkibidiUlysse/meteo-dashboard.git
cd meteo-dashboard

pip install requests
python meteo.py
# → Generates bulletin + opens dashboard in browser
```

## Roadmap

- [ ] **Agentic outfit recommendation** — AI-powered clothing suggestions based on full-day forecast (morning commute vs. afternoon vs. evening), activity type, and personal style preferences
- [ ] **Smart wardrobe integration** — connect to a wardrobe inventory to suggest specific items you own
- [ ] **7-day forecast view** — extended forecast with daily cards
- [ ] **Hourly timeline** — interactive hour-by-hour temperature & precipitation chart
- [ ] **City search** — add any city worldwide via search
- [ ] **PWA support** — installable as a mobile app
- [ ] **Weather alerts** — push notifications for extreme conditions
- [ ] **Historical comparison** — "today vs. same day last year"

---

<p align="center"><em>Weather, but beautiful.</em></p>
