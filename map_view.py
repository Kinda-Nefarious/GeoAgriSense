"""
GeoAgriSense - farm map view
Loads the demo dataset (data/blocks.geojson, data/observations.geojson,
data/farm_boundary.geojson) and renders them on an interactive Leaflet
map inside Streamlit using streamlit-folium.

Usage from app.py:

    from map_view import render_farm_map
    render_farm_map()
"""

import base64
import json
from pathlib import Path

import folium
import streamlit as st
from streamlit_folium import st_folium

DATA_DIR = Path(__file__).parent / "data"
PHOTOS_DIR = DATA_DIR / "photos"

# Risk-level colors, matching the proposal's legend
SEVERITY_COLORS = {
    "Low": "#2ecc71",  # green
    "Watch": "#f1c40f",  # yellow
    "Investigate": "#e67e22",  # orange
    "High": "#e74c3c",  # red
}


def load_geojson(filename):
    path = DATA_DIR / filename
    with open(path, "r") as f:
        return json.load(f)


def photo_to_data_uri(photo_filename):
    """Reads an image from data/photos and returns a base64 data URI,
    so it displays inline in the popup regardless of static file serving."""
    if not photo_filename:
        return None
    path = DATA_DIR / photo_filename
    if not path.exists():
        return None
    ext = path.suffix.lstrip(".").lower()
    mime = "jpeg" if ext == "jpg" else ext
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/{mime};base64,{encoded}"


def render_farm_map():
    st.subheader("🌍 Farm map")

    blocks = load_geojson("blocks.geojson")
    observations = load_geojson("observations.geojson")
    farm_boundary = load_geojson("farm_boundary.geojson")

    # Center the map on the farm boundary's approximate centroid
    coords = farm_boundary["features"][0]["geometry"]["coordinates"][0]
    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    center = [sum(lats) / len(lats), sum(lons) / len(lons)]

    m = folium.Map(location=center, zoom_start=17, tiles="OpenStreetMap")

    # Farm boundary outline
    folium.GeoJson(
        farm_boundary,
        name="Farm boundary",
        style_function=lambda feature: {
            "color": "#34495e",
            "weight": 3,
            "fill": False,
        },
    ).add_to(m)

    # Block polygons, colored by status, with a popup showing details
    def block_style(feature):
        return {
            "fillColor": "#3498db",
            "color": "#2980b9",
            "weight": 2,
            "fillOpacity": 0.15,
        }

    for feature in blocks["features"]:
        props = feature["properties"]
        popup_html = (
            f"<b>{props['name']}</b> ({props['block_id']})<br>"
            f"Crop: {props['crop']}<br>"
            f"Area: {props['approx_area_ha']} ha<br>"
            f"Planted: {props['planting_date']}<br>"
            f"Status: {props['status']}"
        )
        folium.GeoJson(
            feature,
            style_function=block_style,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=props["block_id"],
        ).add_to(m)

    # Observation points, colored by severity, with photo in popup
    for feature in observations["features"]:
        props = feature["properties"]
        lon, lat = feature["geometry"]["coordinates"]
        color = SEVERITY_COLORS.get(props["severity"], "#7f8c8d")

        photo_uri = photo_to_data_uri(props.get("photo_filename"))
        photo_html = (
            f'<img src="{photo_uri}" width="220" style="border-radius:6px;margin-top:6px;"><br>'
            if photo_uri
            else ""
        )

        popup_html = (
            f"<b>{props['observation_id']}</b> — {props['block_id']}<br>"
            f"Symptom: {props['symptom']}<br>"
            f"Severity: <b>{props['severity']}</b><br>"
            f"Date: {props['datetime']}<br>"
            f"Notes: {props.get('notes', '')}<br>"
            f"{photo_html}"
        )
        folium.CircleMarker(
            location=[lat, lon],
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            popup=folium.Popup(popup_html, max_width=280),
            tooltip=f"{props['symptom']} ({props['severity']})",
        ).add_to(m)

    # Legend
    st.caption("🟢 Low   🟡 Watch   🟠 Investigate   🔴 High")

    st_folium(m, width=None, height=550, returned_objects=[])
