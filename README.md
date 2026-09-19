# 🌱 GeoAgriSense

### Spatial Intelligence + Multimodal AI for Agricultural Field Scouting

GeoAgriSense is an agricultural decision-support prototype that combines geospatial farm information, structured field observations and Google's Gemini multimodal AI to help farmers and field scouts identify and prioritise crop problems.

The project was developed during Hack for Humanity Harare 2026 under the **Best Use of the Google Gemini API** challenge.

---

## The Problem

Farmers and field scouts need to identify crop problems early and determine which areas require attention.

Traditional scouting can produce useful observations, but these observations may remain disconnected from their geographic location and from the photographs captured in the field.

GeoAgriSense explores how spatial information and multimodal AI can be combined into one practical scouting workflow.

---

## The Solution

GeoAgriSense provides a dashboard where users can:

- view farm boundaries and production blocks;
- view georeferenced field observations;
- inspect crop and field observations;
- explore observation severity;
- ask Gemini agricultural questions;
- upload a crop photograph;
- combine the photograph with structured field observation data;
- obtain an AI-generated scouting assessment and recommended field checks.

The system is designed as decision support rather than a replacement for agricultural experts.

---

## Key Feature

### Multimodal Gemini Crop Analysis

The user selects a field observation and uploads a crop photograph.

GeoAgriSense sends Gemini:

- the crop photograph;
- crop information;
- production block;
- reported symptom;
- severity;
- field notes;
- observation date where available;
- geographic coordinates where available.

Gemini analyses the visual information together with the field context and returns a structured scouting report containing:

1. Visual observations
2. Crop condition
3. Possible causes
4. Risk assessment
5. Recommended field checks
6. Recommended next action
7. Limitations

This is the core Gemini API integration demonstrated by the prototype.

---

## Technology Stack

- Python
- Streamlit
- Folium
- Streamlit-Folium
- Pandas
- GeoPandas
- GeoJSON
- Google Gemini API
- Google GenAI Python SDK
- python-dotenv

---

## Application Architecture

```text
                 ┌──────────────────────┐
                 │      User / Scout    │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │     Streamlit UI     │
                 └──────────┬───────────┘
                            │
            ┌───────────────┼────────────────┐
            │               │                │
            ▼               ▼                ▼
      Farm/Block Data   Observations     Crop Image
            │               │                │
            └───────────────┼────────────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │   Gemini API Layer   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ AI Scouting Report   │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Farmer / Field Scout │
                 └──────────────────────┘


## PROJECT STRUCTURE

GeoAgriSense/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
│
├── services/
│   ├── __init__.py
│   ├── gemini_service.py
│   └── scouting.py
│
└── data/
    ├── farm_boundary.geojson
    ├── blocks.geojson
    ├── observations.geojson
    └── sample_scouting.csv

## Installation
1. Clone the repository
git clone <GITHUB_REPOSITORY_URL>
cd GeoAgriSense
2. Create a virtual environment

Windows:

python -m venv .venv
.venv\Scripts\activate

Linux/macOS:

python3 -m venv .venv
source .venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
4. Configure Gemini

Create a .env file in the project root:

GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GEMINI_MODEL=gemini-3.6-flash

Never commit .env to GitHub.

5. Run the application
python -m streamlit run app.py

The application will normally be available at:

http://localhost:8501
Gemini API Integration

Gemini is not used merely as a coding assistant.

It is an active component of the application.

The prototype uses the Gemini API for two primary workflows.

1. Agricultural question answering

The user submits a question through the application.

The question is sent to Gemini with an agricultural decision-support instruction.

Gemini returns an explanation and practical field checks.

2. Multimodal crop analysis

The user selects a field observation and uploads a crop photograph.

The application combines:

Photograph
+
Field Observation
+
Crop
+
Block
+
Symptom
+
Severity
+
Notes
+
Location

and sends the combined context to Gemini.

Gemini returns an agricultural scouting assessment.

The application displays the response directly to the user.

Data

The prototype uses structured geospatial demonstration data supplied and developed by the team.

The data includes farm-level and observation-level information such as:

farm boundaries;
production blocks;
crop information;
field observations;
observation severity;
geographic coordinates;
scouting measurements where available.

The current prototype should not be interpreted as a live production farm monitoring system.

Testing

The following prototype components were tested during development:

Python environment;
application startup;
Streamlit interface;
geospatial data loading;
farm map rendering;
observation rendering;
field observation selection;
Gemini API authentication;
Gemini text generation;
Gemini multimodal image analysis;
crop image upload.
Limitations

The current prototype has several limitations.

AI limitations

Gemini's output may be incorrect or incomplete.

A photograph alone cannot reliably establish every plant disease, pest or nutrient deficiency.

The AI output should therefore be treated as decision support rather than definitive agricultural diagnosis.

Data limitations

The prototype uses demonstration data rather than continuous live farm telemetry.

Infrastructure limitations

The prototype does not yet provide a complete production IoT infrastructure for automated soil, weather and crop monitoring.

Connectivity

Gemini analysis requires connectivity to the Gemini API.

Scalability

The current application is an MVP and requires further engineering before production deployment.

Responsible AI

GeoAgriSense is designed with human oversight in mind.

Important considerations include:

AI recommendations should be verified before significant interventions;
the system should not present uncertain diagnoses as established facts;
sensitive farm information should be protected;
API credentials must not be exposed;
users should understand that AI outputs can be wrong;
agricultural professionals should remain involved in high-impact decisions.
Future Development

Future versions could include:

real-time IoT sensor integration;
weather data;
satellite imagery;
vegetation-index analysis;
automated anomaly detection;
historical disease mapping;
field-level risk scoring;
offline-first mobile scouting;
automated alerts;
farm management records;
agronomist review workflows;
temporal crop-health analysis;
predictive crop-risk modelling.

Team

Team Name: Group 2

Team Members
Member	Role / Contribution
Butholethu Mthokozisi Dube - Team Lead / Application & Gemini Integration / Testing
Rufaro Nyakudya - Pitch / Documentation 
Thembelihle Michelle Ndebele - Product Researcher
Shaun Jeranyama - Data / GIS Assistant
Tichaona B. Wutete - UI/UX + Visual Design


Hackathon

Built for:

Hack for Humanity Harare 2026

Challenge:

Best Use of the Google Gemini API


Disclaimer

GeoAgriSense is a hackathon prototype developed for demonstration and experimentation.

AI-generated agricultural recommendations should be independently verified before treatment or other consequential farming decisions are made.