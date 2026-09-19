import json
from pathlib import Path

import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

from services.gemini_service import GeminiService
from services.scouting import (
    prepare_observations,
    scouting_summary,
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

DEFAULT_CSV = DATA_DIR / "sample_scouting.csv"
DEFAULT_GEOJSON = DATA_DIR / "demo_field.geojson"


st.set_page_config(
    page_title="GeoAgriSense MVP",
    page_icon="🌱",
    layout="wide",
)


# ============================================================
# HELPERS
# ============================================================

@st.cache_data
def load_observations(path):
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)

    return prepare_observations(df)


@st.cache_data
def load_geojson(path):
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@st.cache_resource
def get_gemini():
    try:
        return GeminiService()
    except Exception:
        return None


def create_map(df, geojson=None):

    if df.empty:
        center = [-17.8, 31.0]
    else:
        center = [
            float(df["latitude"].mean()),
            float(df["longitude"].mean()),
        ]

    fmap = folium.Map(
        location=center,
        zoom_start=15,
        control_scale=True,
    )

    # Field boundary
    if geojson:

        folium.GeoJson(
            geojson,
            name="Farm boundary",
            style_function=lambda feature: {
                "fillColor": "#2e7d32",
                "color": "#1b5e20",
                "weight": 2,
                "fillOpacity": 0.12,
            },
            tooltip="Field boundary",
        ).add_to(fmap)

    # Scouting points
    for _, row in df.iterrows():

        risk = str(row.get("risk", "Unknown"))

        if risk == "High":
            color = "red"
        elif risk == "Medium":
            color = "orange"
        else:
            color = "green"

        popup = f"""
        <b>{row.get('point_id', 'Unknown')}</b><br>
        Crop: {row.get('crop', 'Unknown')}<br>
        Soil moisture: {row.get('soil_moisture_pct', '-')}%<br>
        Temperature: {row.get('temperature_c', '-')} °C<br>
        Vegetation index: {row.get('vegetation_index', '-')}<br>
        Pest pressure: {row.get('pest_pressure_pct', '-')}%<br>
        Risk: <b>{risk}</b>
        """

        folium.Marker(
            location=[
                float(row["latitude"]),
                float(row["longitude"]),
            ],
            popup=folium.Popup(popup, max_width=350),
            tooltip=f"{row.get('point_id')} — {risk} risk",
            icon=folium.Icon(
                color=color,
                icon="leaf",
                prefix="fa",
            ),
        ).add_to(fmap)

    folium.LayerControl().add_to(fmap)

    return fmap


# ============================================================
# DATA
# ============================================================

df = load_observations(DEFAULT_CSV)

if df.empty:

    df = pd.DataFrame(
        [
            {
                "point_id": "SP-01",
                "crop": "Lettuce",
                "latitude": -17.800,
                "longitude": 31.000,
                "soil_moisture_pct": 72,
                "temperature_c": 24.1,
                "vegetation_index": 0.78,
                "pest_pressure_pct": 8,
            },
            {
                "point_id": "SP-02",
                "crop": "Lettuce",
                "latitude": -17.801,
                "longitude": 31.001,
                "soil_moisture_pct": 54,
                "temperature_c": 26.8,
                "vegetation_index": 0.64,
                "pest_pressure_pct": 24,
            },
            {
                "point_id": "SP-03",
                "crop": "Lettuce",
                "latitude": -17.802,
                "longitude": 31.002,
                "soil_moisture_pct": 31,
                "temperature_c": 29.2,
                "vegetation_index": 0.48,
                "pest_pressure_pct": 58,
            },
            {
                "point_id": "SP-04",
                "crop": "Red cabbage",
                "latitude": -17.799,
                "longitude": 31.003,
                "soil_moisture_pct": 45,
                "temperature_c": 27.6,
                "vegetation_index": 0.59,
                "pest_pressure_pct": 36,
            },
            {
                "point_id": "SP-05",
                "crop": "Red cabbage",
                "latitude": -17.798,
                "longitude": 31.001,
                "soil_moisture_pct": 68,
                "temperature_c": 25.2,
                "vegetation_index": 0.73,
                "pest_pressure_pct": 12,
            },
            {
                "point_id": "SP-06",
                "crop": "Lettuce",
                "latitude": -17.803,
                "longitude": 31.000,
                "soil_moisture_pct": 38,
                "temperature_c": 28.4,
                "vegetation_index": 0.53,
                "pest_pressure_pct": 47,
            },
        ]
    )

    df = prepare_observations(df)


geojson = load_geojson(DEFAULT_GEOJSON)

summary = scouting_summary(df)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("GeoAgriSense MVP")

    st.success("Core application loaded")

    st.subheader("Demo controls")

    uploaded_boundary = st.file_uploader(
        "Upload field boundary / GeoJSON",
        type=["geojson", "json"],
        help="Upload a farm boundary for spatial visualization.",
    )

    if uploaded_boundary:

        try:

            geojson = json.load(uploaded_boundary)

            st.success("Field boundary loaded.")

        except Exception as exc:

            st.error(f"Invalid GeoJSON: {exc}")

    st.divider()

    st.subheader("System status")

    gemini = get_gemini()

    if gemini:

        st.success("Gemini API key loaded")

        st.caption(
            f"Model: `{gemini.model}`"
        )

    else:

        st.error("Gemini API not configured")

    st.divider()

    st.caption(
        "Demo measurements are synthetic and are not measurements "
        "from Sunnyside Farm."
    )


# ============================================================
# HEADER
# ============================================================

st.title("🌱 GeoAgriSense")

st.caption(
    "AI-powered spatial intelligence for smarter farm scouting."
)


st.divider()


# ============================================================
# KPI DASHBOARD
# ============================================================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Scouting points",
        summary["points"],
    )

with col2:
    st.metric(
        "High-risk points",
        summary["high_risk"],
    )

with col3:
    st.metric(
        "Average soil moisture",
        f"{summary['avg_moisture']}%",
    )

with col4:
    st.metric(
        "Average vegetation index",
        summary["avg_vegetation"],
    )


st.info(
    "Demo mode: the scouting measurements shown here are synthetic "
    "demonstration data."
)


# ============================================================
# TABS
# ============================================================

tab_dashboard, tab_map, tab_scout, tab_ai, tab_image = st.tabs(
    [
        "📊 Dashboard",
        "🗺️ Spatial Map",
        "🔎 Scout Analysis",
        "🤖 AI Assistant",
        "📷 Crop Image Analysis",
    ]
)


# ============================================================
# DASHBOARD
# ============================================================

with tab_dashboard:

    st.header("Field overview")

    col_left, col_right = st.columns([1, 1])

    with col_left:

        st.subheader("Risk distribution")

        risk_counts = (
            df["risk"]
            .value_counts()
            .reindex(
                ["High", "Medium", "Low"],
                fill_value=0,
            )
        )

        st.bar_chart(risk_counts)

    with col_right:

        st.subheader("Scouting observations")

        display_columns = [
            "point_id",
            "crop",
            "soil_moisture_pct",
            "temperature_c",
            "vegetation_index",
            "pest_pressure_pct",
            "risk",
        ]

        available_columns = [
            c for c in display_columns
            if c in df.columns
        ]

        st.dataframe(
            df[available_columns],
            use_container_width=True,
            hide_index=True,
        )


# ============================================================
# SPATIAL MAP
# ============================================================

with tab_map:

    st.header("Spatial field intelligence")

    st.write(
        "GeoAgriSense combines scouting observations with geographic "
        "location to identify where intervention may be required."
    )

    fmap = create_map(
        df,
        geojson,
    )

    st_folium(
        fmap,
        width=None,
        height=600,
        returned_objects=[],
    )


# ============================================================
# SCOUT ANALYSIS
# ============================================================

with tab_scout:

    st.header("Scout Analysis")

    high_risk = df[df["risk"] == "High"]

    if high_risk.empty:

        st.success(
            "No high-risk scouting points detected."
        )

    else:

        st.warning(
            f"{len(high_risk)} high-risk scouting point(s) "
            "require attention."
        )

        for _, row in high_risk.iterrows():

            with st.expander(
                f"{row['point_id']} — {row['crop']} — HIGH RISK"
            ):

                c1, c2, c3 = st.columns(3)

                with c1:
                    st.metric(
                        "Soil moisture",
                        f"{row['soil_moisture_pct']}%",
                    )

                with c2:
                    st.metric(
                        "Vegetation index",
                        row["vegetation_index"],
                    )

                with c3:
                    st.metric(
                        "Pest pressure",
                        f"{row['pest_pressure_pct']}%",
                    )

                st.markdown(
                    """
                    **Suggested field action**

                    1. Visit the location as a priority.
                    2. Inspect leaves and growing points.
                    3. Check soil moisture and irrigation performance.
                    4. Scout for visible pests or disease symptoms.
                    5. Capture a photograph for AI-assisted assessment.
                    """
                )


# ============================================================
# TEXT AI ASSISTANT
# ============================================================

with tab_ai:

    st.header("🤖 GeoAgriSense AI Assistant")

    st.write(
        "Ask Gemini an agricultural or crop-scouting question."
    )

    question = st.text_area(
        "Question",
        value=(
            "What should a farmer check when lettuce shows "
            "wilting despite recent irrigation?"
        ),
        height=120,
    )

    if st.button(
        "Ask GeoAgriSense",
        type="primary",
        key="ask_ai",
    ):

        if not question.strip():

            st.warning("Please enter a question.")

        elif not gemini:

            st.error(
                "Gemini is not configured. Check GEMINI_API_KEY."
            )

        else:

            with st.spinner("GeoAgriSense is consulting Gemini..."):

                answer = gemini.ask(
                    question.strip()
                )

            st.markdown(answer)


# ============================================================
# IMAGE ANALYSIS
# ============================================================

with tab_image:

    st.header("📷 AI Crop Image Analysis")

    st.write(
        "Upload a photograph captured during field scouting. "
        "GeoAgriSense will send the image to Gemini for visual "
        "agricultural assessment."
    )

    st.info(
        "For the hackathon demonstration, use a clear close-up "
        "photograph showing leaves, stems, fruit or other visible "
        "crop symptoms."
    )

    col1, col2 = st.columns([1, 1])

    with col1:

        crop = st.selectbox(
            "Crop",
            [
                "Lettuce",
                "Red cabbage",
                "Tomato",
                "Covo",
                "Rape",
                "Spinach",
                "Other",
            ],
        )

        location = st.text_input(
            "Field location / scouting point",
            value="Sunnyside demonstration field",
        )

        additional_context = st.text_area(
            "Additional scout observations",
            placeholder=(
                "Example: Lower leaves have started turning yellow "
                "and several plants appear wilted."
            ),
            height=100,
        )

        uploaded_image = st.file_uploader(
            "Upload crop photograph",
            type=[
                "jpg",
                "jpeg",
                "png",
                "webp",
            ],
            key="crop_image",
        )

    with col2:

        if uploaded_image:

            st.image(
                uploaded_image,
                caption="Uploaded scouting photograph",
                use_container_width=True,
            )

        else:

            st.markdown(
                """
                ### What happens here?

                **1. Upload**

                A farmer or field scout captures a crop photograph.

                **2. Context**

                Crop type, location and scout observations are attached.

                **3. AI analysis**

                Gemini analyses the visual evidence.

                **4. Decision support**

                GeoAgriSense returns observations, possible causes,
                risk level and recommended field checks.
                """
            )

    if st.button(
        "🔬 Analyze Crop with Gemini",
        type="primary",
        key="analyze_crop",
    ):

        if not uploaded_image:

            st.warning(
                "Please upload a crop photograph first."
            )

        elif not gemini:

            st.error(
                "Gemini is not configured. Check GEMINI_API_KEY."
            )

        else:

            image_bytes = uploaded_image.getvalue()

            mime_type = uploaded_image.type

            with st.spinner(
                "Gemini is analysing the crop photograph..."
            ):

                result = gemini.analyze_crop_image(
                    image_bytes=image_bytes,
                    mime_type=mime_type,
                    crop=crop,
                    location=location,
                    additional_context=additional_context,
                )

            st.subheader("AI Scouting Report")

            st.markdown(result)

            st.caption(
                "AI-generated agricultural decision support. "
                "Field confirmation and professional agronomic "
                "assessment should be used before applying treatments."
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "GeoAgriSense — Hack for Humanity MVP | "
    "Layered prototype: UI → Data → Spatial Intelligence → AI"
)