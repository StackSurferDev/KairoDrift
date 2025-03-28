# 🌊 KairoAI - Search and Rescue Drift Tracker

**KairoAI** is an AI-enhanced web application that predicts drift patterns in the ocean for search and rescue (SAR) missions. It estimates the position of a person or vessel based on the incident time and coordinates, using live ocean current data and machine learning models.

---

## 🚀 Features

- 🌐 Real-time ocean current integration via **Open-Meteo Marine API** and **Copernicus Marine**
- 📦 Predicts ocean drift from **last known position** and **incident time**
- 🧠 Uses machine learning to recommend search patterns and enhance drift accuracy
- 🗺️ Beautiful **Leaflet.js** map with **animated ocean current overlays**
- 🎯 Recommends the most suitable SAR pattern (e.g., Sector Search, Expanding Square, Parallel Sweep)
- 🧪 FastAPI + Python + xarray + MotuClient + Leaflet = magic

---

## 🗂️ Project Structure

```
KairoDrift/
│
├── main.py                     # Main FastAPI backend logic
├── .env                        # Environment variables (CMEMS credentials)
├── requirements.txt            # All project dependencies
│
├── ml/                         # Machine learning models
│   ├── model_drift.pkl
│   ├── model_pattern.pkl
│   ├── object_encoder.pkl
│   └── pattern_encoder.pkl
│
├── data/                       # Ocean drift NetCDF files (.nc)
│
├── static/                     # Static frontend files
│   ├── style.css               # UI styling
│   ├── map.js                  # Map logic with animated ocean vectors
│   └── current_vectors.json    # Pre-processed animated ocean vector data
│
├── templates/                  # Jinja2 HTML templates
│   ├── index.html              # Input form and map
│   └── result.html             # Prediction results with map overlay
```

---

## 🧪 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/kairoai-drift-tracker.git
cd kairoai-drift-tracker
```

### 2. Create & activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate     # macOS/Linux
venv\Scripts\activate        # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup your `.env` file

Create a `.env` file in the root:

```env
CMEMS_USER=your_copernicus_username
CMEMS_PWD=your_copernicus_password
```

> 🔐 You must have a valid Copernicus Marine account to pull hourly NetCDF ocean data.

---

## ⚡ Run the App

```bash
uvicorn main:app --reload
```

Visit [http://localhost:8000](http://localhost:8000) in your browser.

---

## 🌍 APIs Used

| API | Description |
|-----|-------------|
| [Open-Meteo Marine](https://open-meteo.com/en/docs/marine-weather-api) | Live ocean current speed and direction |
| [Copernicus Marine](https://marine.copernicus.eu/) | Hourly ocean current NetCDF data for advanced drift accuracy |

---

## 🧠 Machine Learning

The app uses:
- A **regression model** to estimate drift distance
- A **classification model** to recommend optimal SAR search pattern
- Trained on historical simulated drift data (Simon's Town and Cape Point)

---

## 📊 Live Map with Currents

The Leaflet map supports:
- Markers for **last known location** and **predicted position**
- Drift line between points
- Animated ocean current overlay via `leaflet-velocity` and `current_vectors.json`

---

## 📸 Screenshot

![KairoAI Screenshot](https://your-screenshot-link-if-you-have-one.com)

---

## 👨‍🚒 Use Case

Originally built for potential adoption by **NSRI South Africa**, this tool is intended for volunteer responders, coastal SAR teams, and marine researchers.

---

## 🛠️ Future Improvements

- Backward drift tracing (inverse modeling)
- Support for wind influence
- Mobile responsiveness
- Integration with live marine traffic

---

## 📃 License

MIT License - free for personal and non-commercial use.

---

## 🙏 Acknowledgements

- Open-Meteo
- Copernicus Marine
- Leaflet.js
- NSRI for the inspiration 🌊
