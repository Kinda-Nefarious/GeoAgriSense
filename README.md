# 🌱 GeoAgriSense

### AI-powered spatial intelligence for smarter farm scouting.

GeoAgriSense is a Hack for Humanity MVP designed to help farmers move from reactive crop management to data-informed scouting and early intervention.

## MVP capabilities

- Interactive Streamlit dashboard
- Crop scouting observations
- Rule-based scouting risk prioritisation
- Spatial visualisation of scouting points
- GeoJSON field-boundary upload
- Gemini-powered agricultural Q&A
- Modular architecture for future IoT, drone and GIS integration

## Architecture

```text
                    GeoAgriSense
                         │
                         ▼
                  Streamlit UI
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
       Data Layer    Spatial Layer    AI Layer
          │              │              │
          ▼              ▼              ▼
     Risk scoring    Folium/GIS      Gemini API
          │              │              │
          └──────────────┼──────────────┘
                         ▼
                 Farmer decision support